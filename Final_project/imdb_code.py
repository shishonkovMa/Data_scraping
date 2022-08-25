from imdb_helper_functions import *
import json
import numpy as np


def get_actors_by_movie_soup(cast_page_soup, num_of_actors_limit=None):
    actors = cast_page_soup.find('table', attrs={'class': 'cast_list'}).find_all('tr')
    actors_list_ = []
    for i in range(1, len(actors)):
        try:
            actor = actors[i].find_all('a')[1]
            actors_list_.append((actor.text.strip(), 'https://www.imdb.com' + actor['href']))
        except IndexError:
            break
    return actors_list_[:num_of_actors_limit]


def get_movies_by_actor_soup(actor_page_soup, num_of_movies_limit=None):
    film = actor_page_soup.find('div', attrs={'id': 'filmo-head-actor'})
    if film is None:
        film = actor_page_soup.find('div', attrs={'id': 'filmo-head-actress'})
    all_movies = film.find_next_sibling('div', attrs={'class': 'filmo-category-section'})\
                     .find_all('div', class_='filmo-row')
    movies_ = []
    for mov in range(len(all_movies)):
        if all_movies[mov].contents[4] == '\n':
            movies_.append((all_movies[mov].contents[3].text,
                            'https://www.imdb.com' +
                            list(all_movies[mov].contents[3].children)[0]['href'] +
                            'fullcredits'))
    return movies_[:num_of_movies_limit]


def get_movie_distance(actor_start_url, actor_end_url,
                       num_of_actors_limit=None, num_of_movies_limit=None):

    try:
        with open('actor_seen_all.json') as f:
            actor_seen_all = json.load(f)
    except FileNotFoundError:
        actor_seen_all = dict()

    try:
        with open('movie_seen_all.json') as f:
            movie_seen_all = json.load(f)
    except FileNotFoundError:
        movie_seen_all = dict()

    if actor_end_url[0] == 'i':
        actor_end_url = 'https://www.' + actor_end_url

    actors_list = {actor_start_url}

    actor_seen = dict()
    cur_actors_list = set()
    cur_actors_list.update(actors_list)

    movie_seen = dict()
    cur_movies_list = set()

    # For a common task
    limit = 10
    # For a local task
    # limit = 3

    for dist in range(1, limit+1):

        movies_list = set()
        for act in actors_list:
            try:
                m = actor_seen_all[act]
            except KeyError:
                m = list(np.array(get_movies_by_actor_soup(from_url_return_soup(act),
                                                           num_of_movies_limit))[:, 1])
            actor_seen[act] = m
            movies_list.update(m)
        movies_list -= cur_movies_list
        cur_movies_list.update(movies_list)

        actor_seen_all.update(actor_seen)
        with open('actor_seen_all.json', "w", encoding="utf-8") as f:
            json.dump(actor_seen_all, f)

        actors_list = set()
        for movie in movies_list:
            try:
                a = movie_seen_all[movie]
            except KeyError:
                a = list(np.array(get_actors_by_movie_soup(from_url_return_soup(movie),
                                                           num_of_actors_limit))[:, 1])
            movie_seen[movie] = a
            if actor_end_url in a:
                return dist
            else:
                pass
            actors_list.update(a)
        actors_list -= cur_actors_list
        cur_actors_list.update(actors_list)

        movie_seen_all.update(movie_seen)
        with open('movie_seen_all.json', "w", encoding="utf-8") as f:
            json.dump(movie_seen_all, f)

    return 'inf'


def get_movie_descriptions_by_actor_soup(actor_page_soup):
    list_of_movies = get_movies_by_actor_soup(actor_page_soup)
    list_of_descriptions = []
    for name, url in list_of_movies:
        movie_url = url.replace('fullcredits', 'plotsummary')
        description = from_url_return_soup(movie_url)\
            .find('li', attrs={'class': 'ipl-zebra-list__item'})\
            .find('p')\
            .text.strip()
        list_of_descriptions.append(description)
    return list_of_descriptions


# Recording files with descriptions of films in which the highest-paid actors of 2019 played

# list_of_actors = [('Dwayne Johnson', 'https://www.imdb.com/name/nm0425005/'),
#                   ('Chris Hemsworth', 'https://www.imdb.com/name/nm1165110/'),
#                   ('Robert Downey Jr', 'https://www.imdb.com/name/nm0000375/'),
#                   ('Akshay Kumar', 'https://www.imdb.com/name/nm0474774/'),
#                   ('Jackie Chan', 'https://www.imdb.com/name/nm0000329/'),
#                   ('Bradley Cooper', 'https://www.imdb.com/name/nm0177896/'),
#                   ('Adam Sandler', 'https://www.imdb.com/name/nm0001191/'),
#                   ('Scarlett Johansson', 'https://www.imdb.com/name/nm0424060/'),
#                   ('Sofia Vergara', 'https://www.imdb.com/name/nm0005527/'),
#                   ('Chris Evans', 'https://www.imdb.com/name/nm0262635/')]
#
# for actor_name, actor_url in list_of_actors:
#     with open(f'{actor_name}.txt', "w", encoding="utf-8") as file:
#         file.writelines(get_movie_descriptions_by_actor_soup(from_url_return_soup(actor_url)))
