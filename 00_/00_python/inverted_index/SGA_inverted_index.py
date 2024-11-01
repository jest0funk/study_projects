"""SGA Inveret Index >>>
Class InvertedIndex implemented as Command Line Interface(CLI)"""

import json
import argparse


class InvertedIndex:
    """A class for article index inversion"""

    def __init__(self, word_to_docs_mapping):
        self.inverted_index_dictionary = word_to_docs_mapping

    def query(self, words):
        """query method takes an iterable as an argument
        and chooses common articles for all words in the query"""
        init_flag = True
        for word in words:
            input_set = set(self.inverted_index_dictionary.get(word, set()))
            if init_flag:
                output_set = input_set
                init_flag = False
            else:
                output_set &= input_set
        return output_set  # set of common article_id for all words

    def dump(self, filepath):
        """dump method saves index dictionary to disk in json format"""
        json_dictionary = {
            word: list(article_id_match)
            for word, article_id_match in self.inverted_index_dictionary.items()
        }
        with open(filepath, "w", encoding="utf8") as _file:
            json.dump(json_dictionary, _file)

    @classmethod
    def load(cls, filepath):
        """load method restores index from file to InvertedIndex object"""
        with open(filepath, "r", encoding="utf8") as _file:
            json_dictionary = json.load(_file)
            inverted_index_dictionary = {
                word: set(article_id_match)
                for word, article_id_match in json_dictionary.items()
            }
        return InvertedIndex(inverted_index_dictionary)  # InvertedIndex object


def load_document(filepath):
    """load_document function takes a file of Wikipedia articles and returns a dictionary
    where the key is article_id and the value is the article content"""
    article_dictionary = dict()
    with open(filepath, "r", encoding="utf8") as _file:
        for line in _file:
            article_string = line.split("\t", maxsplit=1)
            article_dictionary[int(article_string[0])] = article_string[1].strip()
    return article_dictionary  # {article_id: article_content}


def build_inverted_index(articles):
    """build_inverted_index function takes the 'load_document' dunction output
    and returns an InvertedIndex object"""
    inverted_index_dictionary = dict()
    for article_id, article_content in articles.items():
        for word in article_content.split():
            inverted_index_dictionary.setdefault(word, set()).add(article_id)
    return InvertedIndex(inverted_index_dictionary)  # InvertedIndex object


def build(args):
    """build function is called by build command of ArgumentParser below.
    It takes a Wikipedia dump as input, constructs an inverted index and saves it to disk.
    For this purpose corresponding functions and class methods from above are used"""
    build_inverted_index(load_document(args.dataset)).dump(args.index)


def query(args):
    """query function is called by query command of ArgumentParser below.
    It finds common articles for words in each query from a query file.
    For this purpose corresponding functions and class methods from above are used"""
    inverted_index_odject = InvertedIndex.load(args.index)
    with open(args.query_file, "r", encoding="utf8") as _file:
        for line in _file:
            output = ",".join(
                map(str, sorted(list(inverted_index_odject.query(line.split()))))
            )
            print(output)


def parse_args():
    """parse_args function bulds necssary commands for comand line interface"""
    parser = argparse.ArgumentParser(
        description="Comand line interface \
            for Invereted Index class methods and auxillary functions"
    )
    subparsers = parser.add_subparsers(
        dest="command", help="Commands to run", required=True
    )

    build_command = subparsers.add_parser(
        "build",
        help="The build command takes a Wikipedia dump as input, \
            constructs an inverted index and saves it to disk.",
    )
    build_command.add_argument(
        "--dataset", help="path to dataset to build Inverted Index"
    )
    build_command.add_argument("--index", help="path for Inverted Index dump")
    build_command.set_defaults(func=build)

    query_command = subparsers.add_parser(
        "query",
        help="The query command must find common articles \
            for words in each query from the query file.",
    )
    query_command.add_argument("--index", help="path to load Inverted Index")
    query_command.add_argument(
        "--query_file",
        help="query_file with collection of queries to run against Inverted Index",
    )
    query_command.set_defaults(func=query)

    return parser.parse_args()


def main():
    """Coommand line prompt target"""
    args = parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
