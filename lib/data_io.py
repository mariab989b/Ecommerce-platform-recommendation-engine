# lib/data_io.py
# Excel store robuste :
# - Timeout de verrou (3s) + messages clairs
# - Écritures non réentrantes (un seul verrou par opération)
# - Transaction atomique multi-feuilles via transactional_update()

import os
from typing import Dict, Callable
import pandas as pd
from filelock import FileLock, Timeout

DEFAULT_SHEETS = {
    'users': ['id', 'email', 'password', 'role'],
    'products': ['id', 'name', 'category', 'price', 'currency', 'stock', 'image_url', 'active', 'image_path'],
    'orders': ['id', 'user_id', 'created_at', 'total', 'status', 'payment_txn_id'],
    'order_items': ['order_id', 'product_id', 'qty', 'unit_price'],
    'events': ['id', 'ts', 'user_id', 'type', 'payload_json'],
}

LOCK_TIMEOUT_SECS = 3


class ExcelStore:
    def __init__(self, path: str):
        self.path = path
        self.lock_path = f"{path}.lock"
        os.makedirs(os.path.dirname(path), exist_ok=True)
        if not os.path.exists(path):
            self._create_empty_workbook()

    # ---------- low-level ----------
    def _create_empty_workbook(self):
        with pd.ExcelWriter(self.path, engine='openpyxl', mode='w') as writer:
            for sheet, cols in DEFAULT_SHEETS.items():
                pd.DataFrame(columns=cols).to_excel(writer, sheet_name=sheet, index=False)

    def _read_all(self) -> Dict[str, pd.DataFrame]:
        dfs = pd.read_excel(self.path, sheet_name=None)
        # assurer présence/alignement des feuilles/colonnes
        changed = False
        for s, cols in DEFAULT_SHEETS.items():
            if s not in dfs:
                dfs[s] = pd.DataFrame(columns=cols)
                changed = True
            else:
                for c in cols:
                    if c not in dfs[s].columns:
                        dfs[s][c] = None
                dfs[s] = dfs[s][cols]
        if changed:
            self._write_all(dfs)
        return dfs

    def _write_all(self, dfs: Dict[str, pd.DataFrame]):
        with pd.ExcelWriter(self.path, engine='openpyxl', mode='w') as writer:
            for name, df in dfs.items():
                df.to_excel(writer, sheet_name=name, index=False)

    # ---------- public API ----------
    def read(self, sheet: str) -> pd.DataFrame:
        dfs = self._read_all()
        return dfs.get(sheet, pd.DataFrame(columns=DEFAULT_SHEETS[sheet]))

    def write(self, sheet: str, df: pd.DataFrame):
        try:
            with FileLock(self.lock_path, timeout=LOCK_TIMEOUT_SECS):
                dfs = self._read_all()
                cols = DEFAULT_SHEETS[sheet]
                for c in cols:
                    if c not in df.columns:
                        df[c] = None
                dfs[sheet] = df[cols]
                self._write_all(dfs)
        except Timeout:
            raise RuntimeError("Data file is locked. Close Excel or retry in a moment.")

    def append(self, sheet: str, row_dict: Dict):
        try:
            with FileLock(self.lock_path, timeout=LOCK_TIMEOUT_SECS):
                dfs = self._read_all()
                base = dfs.get(sheet, pd.DataFrame(columns=DEFAULT_SHEETS[sheet]))
                base = pd.concat([base, pd.DataFrame([row_dict])], ignore_index=True)

                cols = DEFAULT_SHEETS[sheet]
                for c in cols:
                    if c not in base.columns:
                        base[c] = None
                dfs[sheet] = base[cols]

                self._write_all(dfs)
        except Timeout:
            raise RuntimeError("Data file is locked. Close Excel or retry in a moment.")

    def transactional_update(self, apply_fn: Callable[[Dict[str, pd.DataFrame]], Dict[str, pd.DataFrame]]):
        """
        Exécute apply_fn(dfs) sous un seul verrou, puis écrit toutes les feuilles.
        apply_fn doit retourner le dict dfs modifié (aligné si possible).
        """
        try:
            with FileLock(self.lock_path, timeout=LOCK_TIMEOUT_SECS):
                dfs = self._read_all()
                new_dfs = apply_fn(dfs)
                # réaligner toutes les feuilles selon DEFAULT_SHEETS
                for s, cols in DEFAULT_SHEETS.items():
                    if s not in new_dfs:
                        new_dfs[s] = pd.DataFrame(columns=cols)
                    else:
                        for c in cols:
                            if c not in new_dfs[s].columns:
                                new_dfs[s][c] = None
                        new_dfs[s] = new_dfs[s][cols]
                self._write_all(new_dfs)
        except Timeout:
            raise RuntimeError("Data file is locked. Close Excel or retry in a moment.")

    def next_id(self, sheet: str) -> int:
        df = self.read(sheet)
        if df.empty:
            return 1
        key = 'id' if 'id' in df.columns else df.columns[0]
        return int(pd.to_numeric(df[key], errors='coerce').fillna(0).max()) + 1
