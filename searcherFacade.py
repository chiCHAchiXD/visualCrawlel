from searcher_ import Searcher
class SearcherFacade:
    def __init__(self):
        self.searcher = Searcher()

    def visit(self, stuff, dementor=',', save_to=r'.\saved'):
        self.searcher.set_path(save_to)
        self.searcher.set_dementor(dementor)
        self.searcher.set_words(stuff)
        self.searcher.search_all_words()

