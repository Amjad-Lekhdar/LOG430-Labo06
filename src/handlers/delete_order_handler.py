"""
Handler: delete order
SPDX - License - Identifier: LGPL - 3.0 - or -later
Auteurs : Gabriel C. Ullmann, Fabio Petrillo, 2025
"""
import requests
import config
from handlers.handler import Handler
from order_saga_state import OrderSagaState

class DeleteOrderHandler(Handler):
    """ Handle order deletion. """

    def __init__(self, order_id):
        """ Constructor method """
        self.order_id = order_id
        super().__init__()

    def run(self):
        """Call StoreManager to check out from stock"""
        # TODO: utilisez l'ID de la commande pour la supprimer (vous pouvez utiliser les autres handlers comme réference d'implementation)
        response = requests.delete(f'{config.API_GATEWAY_URL}/order-manager-api/orders/{self.order_id}')
        if response.ok:
            self.logger.debug(f"Commande {self.order_id} supprimée avec succès.")
        else:
            self.logger.error(f"Échec de la suppression de la commande {self.order_id}.")
            
        self.logger.debug(f"Transition d'état: DeleteOrder -> ORDER_DELETED")
        return OrderSagaState.ORDER_DELETED
        
    def rollback(self):
        """
        (rollback not applicable for DeleteOrder)
        """
        # Nous héritons de la classe abstraite Handler, et par conséquent, l'implémentation de la méthode rollback() est obligatoire.
        pass
