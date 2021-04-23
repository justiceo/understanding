from multiprocessing.managers import BaseManager

GENSIM_PORT = 9100

class Gensim:
    """
    Interface to interacting with Gensim Rest API.
    TODO: Dockerize https://github.com/alibugra/flask-gensim
    """

    def init(self, port=GENSIM_PORT):
        """
        Issues a call to the server with a hardcoded text, prints the return status.
        Returns true if server returned OK.
        """
        self.manager = BaseManager(address=('localhost', GENSIM_PORT), authkey=b'random auth')
        self.manager.connect()
        return False

    
    def most_similar(self, terms):
        (requests_queue, response_queue) = self.get_queues()
        requests_queue.put(terms)
        return response_queue.get()

    
    def get_queues(self):
        BaseManager.register('terms_queue')
        BaseManager.register('similarities_queue')
        

        terms_request_queue = self.manager.terms_queue()
        similarities_response_queue = self.manager.similarities_queue()
        return (terms_request_queue, similarities_response_queue)




if __name__ == "__main__":
    g = Gensim()
    g.init()
    print(g.most_similar(["barack", "obama"]))
