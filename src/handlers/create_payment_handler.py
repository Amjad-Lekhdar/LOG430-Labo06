"""
Handler: create payment transaction
SPDX - License - Identifier: LGPL - 3.0 - or -later
Auteurs : Gabriel C. Ullmann, Fabio Petrillo, 2025
"""
import requests
import config
from handlers.handler import Handler
from order_saga_state import OrderSagaState

class CreatePaymentHandler(Handler):
    """ Handle the creation of a payment transaction for a given order. Trigger rollback of previous steps in case of failure. """

    def __init__(self, order_id, order_data):
        """ Constructor method """
        self.order_id = order_id
        self.order_data = order_data
        self.total_amount = 0
        super().__init__()

    def run(self):
        """Call payment microservice to generate payment transaction"""
        try:
            # TODO: effectuer une requête à /orders pour obtenir le total_amount de la commande (que sera utilisé pour démander la transaction de paiement)
            """
            GET my-api-gateway-address/order/{id} ...
            """

            response = requests.get(f'{config.API_GATEWAY_URL}/order-manager-api/orders/{self.order_id}')
            if response.ok:
                order_info = response.json()
                self.total_amount = order_info.get('total_amount', 0)
            else:
                self.logger.error(f"Échec de la récupération des informations de la commande {self.order_id}.")
                return self.rollback()

            # TODO: effectuer une requête à /payments pour créer une transaction de paiement
            """
            POST my-api-gateway-address/payments ...
            json={ voir collection Postman pour en savoir plus ... }
            """
            response = requests.post(f'{config.API_GATEWAY_URL}/payment-manager-api/payments', 
            json={
                    "order_id": self.order_id,
                    "amount": self.total_amount
                },
                headers={'Content-Type': 'application/json'}
            )
            if response.ok:
                self.logger.debug("Transition d'état: CreatePayment -> PAYMENT_CREATED")
                return OrderSagaState.PAYMENT_CREATED
            else:
                return self.rollback()

        except Exception:
            return self.rollback()
        
    def rollback(self):
        """ Call StoreManager to restore stock quantities if payment transaction creation fails """
        # TODO: remettre en stock tous les articles qui avaient été retirés du stock (dans self.order_data)
        response = requests.put(f'{config.API_GATEWAY_URL}/store-manager-api/stocks',
            json={
                    "items": self.order_data["items"],
                    "operation": "+"
                },
                headers={'Content-Type': 'application/json'}
            )
        if response.ok:
            self.logger.debug("Stock restauré avec succès.")
        else:
            self.logger.error("Échec de la restauration du stock.")
        self.logger.debug("Transition d'état: CreatePaymentFailure -> STOCK_INCREASED")
        return OrderSagaState.STOCK_INCREASED