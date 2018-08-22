'''
Created on Jul 16, 2018

@author: profitrolle
'''

from woocommerce import API
import threading
import FB_database_api as dbapi
from time import sleep

# TODO : The method to retrieve boards and update order when they are multiple boards for one order must be updated
# Idea : create in local database a field for each board corresponding to the status. Update the status in wc

READING_TIME_INTERVAL = 60

class WP_Interface():
    
    def __init__(self):
        self.wcapi = API(
            url="http://127.0.0.1/index.php",
            consumer_key="ck_d8f143faa5371aa8e40927134b7df279babdaf59",
            consumer_secret="cs_24fa6f9c569ef3205b4252e904c92601ca759147",
            wp_api=True,
            version="wc/v2"
        )
        # Create thread that reads wp orders every x minutes
        self.do_scrap_orders = True
        self.scrap_orders_t = threading.Thread(target=self.scrapping_thread)
        self.scrap_orders_t.daemon = True
        self.scrap_orders_t.start()

    def update_order_status(self, p_order, p_status):
        data = {"status": p_status}
        self.wcapi.put("orders/" + str(p_order), data).json()

    def retrieve_orders(self):
        orders = self.wcapi.get("orders")
        return orders.json()
    
    def create_orders(self, p_orders_dic):
        """
        @brief: This function retrievec the completed order and returns a list of the 
        job to be done with the description of each board
        """
        for item_order in p_orders_dic:
            # Check if order is payed
            if item_order['status'] == 'completed':
                # Check if already in database
                if not(dbapi.is_wc_order_in_db(item_order['id'])):
                    # Add to local db
                    dbapi.add_order_to_db(item_order)
                    # Update wp status (not sure yet, only when accepted by machine... maybe)
                    # self.update_order_status(int(item_order['id']), 'processing')

    def scrapping_thread(self):
        while self.do_scrap_orders:
            wp_orders = self.retrieve_orders()
            self.create_orders(wp_orders)
            sleep(READING_TIME_INTERVAL)
    
    def update_stock(self):
        pass


if __name__ == '__main__':
    wpinter = WP_Interface()
    data_dict = wpinter.retrieve_orders()
    
