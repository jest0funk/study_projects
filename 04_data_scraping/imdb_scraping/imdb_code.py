# define helper functions if needed
# and put them in `imdb_helper_functions` module.
# you can import them and use here like that:
from imdb_helper_functions import *

import requests
import urllib
import json
from bs4 import BeautifulSoup

from tqdm import tqdm
# import networkx as nx
# import matplotlib.pyplot as plt



def get_actors_by_movie_soup(cast_page_soup, num_of_actors_limit=None):
    cast_table_rows = cast_page_soup.find_all('tr', attrs={'class': ['odd', 'even']})
    canonical_url = get_canonical_url(cast_page_soup)
    movie_actors = [(row.contents[3].text.strip(), 
                     urllib.parse.urljoin(canonical_url, row.contents[3].contents[1]['href'].split('?')[0]))
                     for row in cast_table_rows]
    return movie_actors[:num_of_actors_limit]



def get_movies_by_actor_soup(actor_page_soup, num_of_movies_limit=None, include_voice=True):
    actor_section = actor_page_soup.find('div', attrs={'id': ['filmo-head-actor', 'filmo-head-actress']})
    try:
        movie_section = actor_section.find_next_sibling('div', attrs={'class': 'filmo-category-section'})
        movie_records = movie_section.find_all('div', attrs={'class': ['filmo-row odd', 'filmo-row even']})
        canonical_url = get_canonical_url(actor_page_soup)
        actor_movies = [(record.contents[3].text, 
                            urllib.parse.urljoin(
                            canonical_url, record.contents[3].contents[0]['href'].split('?')[0])) 
                            for record in movie_records 
                            if record.contents[4].text.strip() == ''
                            and (eval('"(voice)" not in record.contents[6]') if not include_voice else True)]
    except:
        return [(None, None)]
    return actor_movies[:num_of_movies_limit]



def get_movie_distance(actor_start_url, actor_end_url, 
                       num_of_actors_limit=None, num_of_movies_limit=None,
                       distance_limit=None, search_sides=1, return_triplets=False, 
                       verbose=False, use_cache=False):

    print(f'\n{"-" * 70}\
         \nRunning with following settings:\
         \n\tnum_of_actors_limit = {num_of_actors_limit} \tdistance_limit = {distance_limit}\
         \n\tnum_of_movies_limit = {num_of_movies_limit} \treturn_triplets = {return_triplets}\
         \n\tsearch_sides = {search_sides}\n{"-" * 70}\n') if verbose else None                 

    global cache 
    cache_reading(cache=cache, verbose=verbose) if use_cache else None

    connection_triplets_pair = [
        [(None, (get_actor_name(actor_start_url), actor_start_url), None)], 
        [(None, (get_actor_name(actor_end_url), actor_end_url), None)]
        ]
    movie_distance = float('inf')

    print(f'\nSearchig distance for \n\t{connection_triplets_pair[0][0][1][0]}\
        \n\tand\n\t{connection_triplets_pair[1][0][1][0]}\n') if verbose else None

    for distance in range(1, distance_limit + 1):
        for idx in range(search_sides):
            print(
                f'# Getting data for DISTANCE {distance} // Searching from the side of * {connection_triplets_pair[idx][0][1][0]}\n'
                ) if verbose else None
            gathered_triplets = tqdm(
                connection_triplets_pair[idx].copy()) if verbose else connection_triplets_pair[idx].copy()
            for gathered_triplet in gathered_triplets:

                connection_triplets_pair[idx], connection_found = get_actor_data_layer(
                                                                    gathered_triplet[1], 
                                                                    connection_triplets_pair[1 - idx][0][1],
                                                                    connection_triplets=connection_triplets_pair[idx], 
                                                                    num_of_movies_limit=num_of_movies_limit, 
                                                                    num_of_actors_limit=num_of_actors_limit,
                                                                    verbose=verbose, use_cache=use_cache)
                if connection_found:
                    print(f'# >>> Connection FOUND >>> the DISTANCE is *** {distance} *** \
                    \n# for ({connection_triplets_pair[0][0][1][0]}, {connection_triplets_pair[1][0][1][0]})\n'
                    ) if verbose else None
                    movie_distance = distance
                    cache_dumping(cache=cache, verbose=verbose) if use_cache else None
                    return movie_distance, connection_triplets_pair[idx] if return_triplets else movie_distance

    if movie_distance == float('inf'):
        print(f'# <<< Distance limit reached <<< NO CONNECTION found \
        \n# for ({connection_triplets_pair[0][0][1][0]}, {connection_triplets_pair[1][0][1][0]})') if verbose else None

    cache_dumping(cache=cache, verbose=verbose) if use_cache else None

    return movie_distance, connection_triplets_pair[idx] if return_triplets else movie_distance




def get_movie_descriptions_by_actor_soup(actor_page_soup):
    actor_movies = get_movies_by_actor_soup(actor_page_soup)
    movie_descriptions = []
    for movie in actor_movies:
        try: 
            movie_page_soup = get_page_soup(movie[1], concat_string='plotsummary/')
            summaries_section = movie_page_soup.find('div', attrs={'data-testid': 'sub-section-summaries'})
            summary_items = summaries_section.find_all('li')
            for summary_item in summary_items: summary_item.span.decompose() if summary_item.span else None
            summary_text = " ".join(summary_item.get_text() for summary_item in summary_items)
            movie_descriptions.append(summary_text)
        except:
            pass
    return movie_descriptions
