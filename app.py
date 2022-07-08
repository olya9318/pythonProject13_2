# app.py

from flask import Flask, request, jsonify
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy

from schemas import movies_schema, movie_schema
import models

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['JSON_AS_ASCII'] = False
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

api = Api(app)
movie_ns = api.namespace('movies')


@movie_ns.route("/")
class MoviesView(Resource):
    def get(self):
        movie_with_genre_and_director = db.session.query(models.Movie.id, models.Movie.title, models.Movie.description,
                                                         models.Movie.rating, models.Movie.trailer,
                                                         models.Genre.name.label('genre'),
                                                         models.Director.name.label('director')).join(
            models.Genre).join(models.Director)
        if 'director_id' in request.args:
            data = request.args.get('director_id')
            movie_with_genre_and_director = movie_with_genre_and_director.filter(
                models.Movie.director_id == data)
        if 'genre_id' in request.args:
            data = request.args.get('genre_id')
            movie_with_genre_and_director = movie_with_genre_and_director.filter(
                models.Movie.genre_id == data)

        all_movies = movie_with_genre_and_director.all()
        return jsonify(movies_schema.dump(all_movies))

    def post(self):
        req_json = request.json
        new_movie = models.Movie(**req_json)
        with db.session.begin():
            db.session.add(new_movie)
        return f"Новый объект с id {new_movie.id} создан!"


@movie_ns.route("/<int:movie_id>")
class MovieView(Resource):
    def get(self, movie_id: int):
        movie = db.session.query(models.Movie.id, models.Movie.title, models.Movie.description,
                                 models.Movie.rating, models.Movie.trailer, models.Genre.name.label('genre'),
                                 models.Director.name.label('director')).join(models.Genre).join(
            models.Director).filter(
            models.Movie.id == movie_id).first()
        if movie:
            return jsonify(movie_schema.dump(movie))
        return "Нет такого фильма", 404

    def patch(self, movie_id: int):
        movie = db.session.query(models.Movie).get(movie_id)
        req_json = request.json
        if 'title' in req_json:
            movie.title = req_json['title']
        elif 'description' in req_json:
            movie.description = req_json['description']
        elif 'trailer' in req_json:
            movie.trailer = req_json['trailer']
        elif 'year' in req_json:
            movie.year = req_json['year']
        elif 'rating' in req_json:
            movie.rating = req_json['rating']
        elif 'genre_id' in req_json:
            movie.genre_id = req_json['genre_id']
        elif 'director_id' in req_json:
            movie.director_id = req_json['director_id']
        db.session.add(movie)
        db.session.commit()
        return f"Объект с id {movie_id} обновлен!", 204

    def put(self, movie_id):
        movie = db.session.query(models.Movie).get(movie_id)
        if not movie:
            return "Нет такого фильма", 404
        req_json = request.json
        movie.title = req_json['title']
        movie.description = req_json['description']
        movie.rating = req_json['rating']
        movie.trailer = req_json['trailer']
        movie.year = req_json['year']
        db.session.add(movie)
        db.session.commit()
        return f"Объект с id {movie_id} обновлен!", 204

    def delete(self, movie_id):
        movie = db.session.query(models.Movie).get(movie_id)
        if not movie:
            return "Нет такого фильма", 404
        db.session.delete(movie)
        db.session.commit()
        return f"Объект с id {movie_id} удален", 204


if __name__ == '__main__':
    app.run(debug=True)
