# Fishstore

A web commerce application for buying fish online. Customers can browse the catalogue, add items to a basket and check out, while the store's stock and orders are managed through an SQL database.

**Live demo:** https://cm1102-fishstore-c25037492-cm1102.apps.containers.cs.cf.ac.uk

## Features

- Browse fish by price and alphabetically.
- Product pages with descripptionn, price, and add to basket.
- Shopping basket and checkout
- Automated confirmation page
- Stock and order data stored in an SQL database

## Tech Stack

| Area | Technology |
| --- | --- |
| Backend | Flask |
| Database | SQL |
| Frontend | JavaScript, CSS, HTML |

## Getting Started

### Prerequisites

- [Python 3.10.4]
- [pip]

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/Oakalope/[repo-name].git
   cd [repo-name]
   ```

2. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Set up the database:

   ```bash
   [command or script that creates the tables and adds sample data]
   ```

4. Run the app:

   ```bash
   flask run
   ```

5. Open `http://127.0.0.1:5000` in your browser.

## Project Structure

```
[repo-name]/
├── app.py            # Flask application and routes
├── templates/        # HTML templates
├── static/           # CSS and JavaScript
├── [database file or schema]
└── requirements.txt
```

*Edit this to match your actual folders.*

## What I Learned

- Designing manageable databases foor ecommerce.
- Simplifying routes and using other tools to reduce the number of routes in the webapp.
- Ran into issues with HTML formatting, played around with a range of different techniques to create an enjoyable UX.

## Future Improvements

- Would like to include email checkout confirmation.
- Would like to add accounts and a favouriting system.

## Author

Oakley Whitehead
[GitHub](https://github.com/Oakalope)
