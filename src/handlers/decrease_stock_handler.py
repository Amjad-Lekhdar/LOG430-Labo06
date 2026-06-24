"""
Handler: decrease stock
SPDX - License - Identifier: LGPL - 3.0 - or -later
Auteurs : Gabriel C. Ullmann, Fabio Petrillo, 2025
"""
from logging import config

import requests
from handlers.handler import Handler
from order_saga_state import OrderSagaState

class DecreaseStockHandler(Handler):
    """ Handle the stock check-out of a given list of products and quantities. Trigger rollback of previous steps in case of failure. """

    def __init__(self, order_id, order_item_data):
        """ Constructor method """
        self.order_id = order_id
        self.order_item_data = order_item_data
        super().__init__()

    def run(self):
        """Call StoreManager to check out from stock"""
        try:
            # TODO: effectuer une requête à /stocks pour diminuer les quantités dans le stock
            response = requests.post(f'{config.API_GATEWAY_URL}/store-manager-api/stocks',
            json={
                    "items": self.order_item_data,
                    "operation": "-"
                },
                headers={'Content-Type': 'application/json'}
            )

            if response.ok:
                self.logger.debug("Transition d'état: DecreaseStock -> STOCK_DECREASED")
                return OrderSagaState.STOCK_DECREASED
            else:
                return self.rollback()
            
        except Exception as e:
            self.logger.error(f"DecreaseStock a échoué : {e}")
            return self.rollback()
        
    def rollback(self):
        """ Call StoreManager to delete order if stock decrease fails """
        # TODO: utilisez l'ID de la commande pour la supprimer
        response = requests.delete(f'{config.API_GATEWAY_URL}/order-manager-api/orders/{self.order_id}')
        if response.ok:
            self.logger.debug(f"Commande {self.order_id} supprimée avec succès.")
        else:
            self.logger.error(f"Échec de la suppression de la commande {self.order_id}.")
            
        self.logger.debug(f"Transition d'état: DecreaseStockFailure -> ORDER_DELETED")
        return OrderSagaState.ORDER_DELETED