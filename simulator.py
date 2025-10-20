# simulator.py
# Générateur d'ordres factices robuste (transactionnel)
from __future__ import annotations
import random
import threading
import time
import pandas as pd
from lib.data_io import ExcelStore

class OrderSimulator:
    def __init__(self, store: ExcelStore, user_email_bot: str = "bot@demo.local"):
        self.store = store
        self.user_email_bot = user_email_bot
        self._thread = None
        self._running = False

    def start(self, orders_per_minute: int, failure_rate: float, max_qty: int):
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(
            target=self._run,
            args=(orders_per_minute, failure_rate, max_qty),
            daemon=True
        )
        self._thread.start()

    def stop(self):
        self._running = False

    def _run(self, opm: int, failure_rate: float, max_qty: int):
        interval = 60.0 / max(1, int(opm))
        while self._running:
            try:
                self._generate_one(failure_rate, max_qty)
            except Exception:
                # on ignore les erreurs ponctuelles pour la boucle
                pass
            time.sleep(interval)

    # ---------------- internals ----------------

    def _generate_one(self, failure_rate: float, max_qty: int):
        """
        Génère une commande transactionnelle :
        - choisit des produits actifs avec stock > 0
        - construit des items
        - applique un statut (PAID/FAILED)
        - décrémente le stock si payé
        - écrit orders + order_items + products en une seule transaction
        """
        # Lecture non verrouillée pour choisir les produits
        prods = self.store.read('products')
        prods = prods[(prods['active'] == True) & (prods['stock'] > 0)]
        if prods.empty:
            return

        # choisir 1–3 produits aléatoires
        n_items = random.randint(1, min(3, len(prods)))
        items_sample = prods.sample(n=n_items)
        qtys = [random.randint(1, max(1, int(max_qty))) for _ in range(n_items)]

        # trouver l'user bot
        users = self.store.read('users')
        bot = users[users['email'].astype(str).str.strip().str.lower() == self.user_email_bot.strip().lower()]
        if bot.empty:
            return
        user_id = int(bot.iloc[0]['id'])

        # calcul statut
        r = random.random()
        status = 'PAID'
        if r < float(failure_rate):
            status = 'FAILED'

        # total TTC approximatif (on ne gère pas la TVA ici pour simplifier le simulateur)
        subtotal = sum(float(p) * q for p, q in zip(items_sample['price'].tolist(), qtys))
        total = round(float(subtotal), 2)

        # --- transaction : une seule prise de verrou ---
        def apply_fn(dfs):
            products = dfs['products']
            orders = dfs['orders']
            order_items = dfs['order_items']

            # allouer un id
            new_order_id = (pd.to_numeric(orders['id'], errors='coerce').fillna(0).max() + 1) if not orders.empty else 1
            order_row = {
                'id': int(new_order_id),
                'user_id': user_id,
                'created_at': pd.Timestamp.utcnow().isoformat(),
                'total': total,
                'status': status,
                'payment_txn_id': f'TXN-{int(new_order_id):06d}',
            }
            orders = pd.concat([orders, pd.DataFrame([order_row])], ignore_index=True)

            # items + décrément stock si payé
            for (idx, prow), qty in zip(items_sample.iterrows(), qtys):
                order_items = pd.concat([order_items, pd.DataFrame([{
                    'order_id': int(new_order_id),
                    'product_id': int(prow['id']),
                    'qty': int(qty),
                    'unit_price': float(prow['price'])
                }])], ignore_index=True)

                if status == 'PAID':
                    mask = products['id'] == prow['id']
                    products.loc[mask, 'stock'] = products.loc[mask, 'stock'].astype(int) - int(qty)

            dfs['orders'] = orders
            dfs['order_items'] = order_items
            dfs['products'] = products
            return dfs

        self.store.transactional_update(apply_fn)
