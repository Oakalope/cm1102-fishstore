from app.FishStore import app, db, Stock

fishes = [
    { "name": "Betta Fish", "price": "22", "description": "Ideal for small tanks but must be kept alone.", "image": "betta.jpg" },
    { "name": "Guppy", "price": "18", "description": "A small, active fish that breeds quickly, ideal for beginners with larger setups.", "image":"guppy.jpg"},
    { "name": "Goldfish", "price": "13", "description": "A fan-favourite, good for beginners and can live outside in well equipped ponds.", "image":"goldfish.jpg"},
    { "name": "Angelfish", "price": "29", "description": "A bit harder to care for, will require a larger tank that's tall.", "image":"angelfish.jpg"}
]

# drop all tables first before creating new empty tables
with app.app_context():
    db.drop_all()
    db.create_all()

    if Stock.query.count() == 0:
        for fish in fishes:
            newFish = Stock(name=fish["name"], price=fish["price"], description=fish["description"], image=fish["image"])
            db.session.add(newFish)

    db.session.commit()

    # checks that the seed works correctly
    all_fish = Stock.query.all()
    for fish in all_fish:
        print(fish.id, fish.name, fish.description, fish.image)