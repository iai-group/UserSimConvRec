import pandas as pd
metadata = pd.read_csv('movies_metadata.csv', low_memory=False)
metadata.head()
print(metadata.isnull().sum())
metadata = metadata.dropna(subset=['imdb_id','poster_path'])
metadata = metadata.drop(['belongs_to_collection','homepage','popularity','tagline','status'],axis=1)
metadata = metadata.drop(['runtime','release_date','original_language','production_countries','production_companies','spoken_languages','video'],axis=1)
import ast
metadata['genres'] = metadata['genres'].apply(lambda x: ast.literal_eval(x))
metadata['genres'] = metadata['genres'].apply(lambda x: ', '.join([d['name'] for d in x]))
metadata['imdbURL'] = 'https://www.imdb.com/title/' + metadata['imdb_id'] + '/'
metadata['tmdbURL'] = 'https://www.themoviedb.org/movie/' + metadata['id']
metadata['ImageURL'] = 'https://image.tmdb.org/t/p/w92' + metadata['poster_path']
metadata.isnull().sum()
metadata.to_csv('metadata_prep.csv')
metadata.head()
