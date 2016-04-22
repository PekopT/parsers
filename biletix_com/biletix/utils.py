import functools


def check_spider_pipeline(process_item_method):
    @functools.wraps(process_item_method)
    def wrapper(self, item, spider):
        if self.__class__ in spider.pipeline:
            return process_item_method(self, item, spider)
        else:
            return item
    return wrapper

def check_spider_close(process_item_method):
    @functools.wraps(process_item_method)
    def wrapper(self, spider):
        if self.__class__ in spider.pipeline:
            return process_item_method(self, spider)
    return wrapper