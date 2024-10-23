# def helper_function_example():
#     return 'Hello, I am a supposed to be a helper function'


cache = {}


def json_read(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
    return data



def json_write(file_path, data):
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=4)  



def cache_reading(cache, verbose=False):
    if len(cache.keys()) == 0:
        print('...Reading cache...') if verbose else None
        try:
            cache = json_read('cache.json')
            cache['cache_size'] = len(cache.keys())
        except FileNotFoundError:
            cache['cache_size'] = 0
        print(f'...Cache size: {len(cache.keys())} entries') if verbose else None
    else: 
        print(f'...No cache updates...\n...Disc reading skipped') if verbose else None



def cache_dumping(cache, verbose=False):
    
    cache_size_current = len(cache.keys())
    if cache_size_current > cache['cache_size']:
        cache['cache_size'] = cache_size_current
        print(f'\n...Dumping cache...\n...Cache size: {cache_size_current} entries') if verbose else None
        json_write('cache.json', data=cache) 
    else:
        print(f'...No cache updates...\n...Dumping skipped') if verbose else None



def get_headers():
    headers = {'Accept-Language': 'en-US;q=0.9,en;q=0.8', 
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) \
               AppleWebKit/537.36 (KHTML, like Gecko) \
               Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.79'}
    return headers



def get_page_from_imdb(url):
    response = requests.get(url, headers=get_headers())
    assert response.status_code == 200
    return response.text



def get_page_soup(url, concat_string='', use_cache=False, force_update=False):
    url += concat_string
    if use_cache:
        global cache
        if url not in cache or force_update:
            cache[url] = get_page_from_imdb(url)
        page_soup = BeautifulSoup(cache[url])
    else:
        page_soup = BeautifulSoup(get_page_from_imdb(url))
    return page_soup



def get_canonical_url(page_soup):
    canonical_url = page_soup.find('link', attrs={'rel': 'canonical'}).attrs['href']
    return canonical_url



def get_actor_name(url):
    actor_page_soup = get_page_soup(url, concat_string='fullcredits/')
    actor_name = actor_page_soup.find(
        'div', attrs={'class': 'name-subpage-header-block'}).find('h3').text.strip()
    return actor_name



def get_actor_url(actor_name):
    url = 'https://www.imdb.com/find/?q=' + actor_name
    search_page_soup = get_page_soup(url)
    canonical_url = get_canonical_url(search_page_soup)
    search_result_section = search_page_soup.find('ul', attrs={
        'class': 'ipc-metadata-list ipc-metadata-list--dividers-after sc-17bafbdb-3 gAWnDM ipc-metadata-list--base'})
    actor_url = search_result_section.find_all('a', attrs={'href': True})[0]['href'].split('?')[0]
    full_actor_url = urllib.parse.urljoin(canonical_url, actor_url)
    return full_actor_url



def get_actor_data_layer(actor, searched_actor, num_of_movies_limit=None, num_of_actors_limit=None,
                         connection_triplets=[], verbose=False, use_cache=False):
    print(f'\n>>> Getting data for\t:\t{actor} \ntriplets before\t:\t{len(connection_triplets)}') if verbose else None
    if any(actor == triplet[0] for triplet in connection_triplets):
        print(f'ACTOR\t:\tSkipping {actor[0]}\n') if verbose else None
    else:
        actor_page_soup = get_page_soup(actor[1], concat_string='fullcredits/', use_cache=use_cache)
        actor_movies = get_movies_by_actor_soup(actor_page_soup, num_of_movies_limit=num_of_movies_limit)
        for movie in actor_movies:
            if not movie[1] or any(movie == triplet[2] for triplet in connection_triplets):
                print(f'MOVIE\t:\tSkipping {movie} for {actor[0]}') if verbose else None
            else:
                cast_page_soup = get_page_soup(movie[1], concat_string='fullcredits/', use_cache=use_cache)
                movie_actors = get_actors_by_movie_soup(cast_page_soup, num_of_actors_limit=num_of_actors_limit)
                for co_actor in movie_actors:
                    if co_actor == actor:
                        print(f'PAIR\t:\tSkipping {actor[0]}, {co_actor[0]} for {movie[0]} // mirrored record') if verbose else None
                    else:
                        triplet = (actor, co_actor, movie)
                        if triplet:
                            connection_triplets.append(triplet)
                        if any(searched_actor == triplet[1] for triplet in connection_triplets):
                            print(f'triplets after\t:\t{len(connection_triplets)}\t<-- connection found\n') if verbose else None
                            return connection_triplets, True
        print(f'triplets after\t:\t{len(connection_triplets)}\n') if verbose else None
    return connection_triplets, False