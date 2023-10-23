from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import pandas as pd
from constants import PRICE_DIFF, VALUE_DIFF

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Load the wine data
df = pd.read_csv('wine.csv')

@app.get("/", response_class=HTMLResponse)
async def choose_wine():
    # Create a datalist with all the wine names
    datalist = '<datalist id="wines">'
    for wine in df['name'].unique():
        datalist += f'<option value="{wine}">'
    datalist += '</datalist>'

    # Create a form with an input field linked to the datalist and a submit button
    form = f'''
    <form action="/recommend_wine" method="post">
        <input type="text" name="wine_name" list="wines" placeholder="Type a wine name">
        <input type="submit" value="Recommend">
    </form>
    '''

    # Add an "Add New Wine" button
    button = '<button onclick="location.href=\'/add_wine\'" type="button">Add New Wine</button>'

    # Link to the CSS file
    styles = '<link rel="stylesheet" href="/static/styles.css">'

    # Return the styles, the form, the datalist, and the button as HTML
    return styles + form + datalist + button

@app.get("/add_wine", response_class=HTMLResponse)
async def add_wine():
    # Create a form with an input field for each column and a submit button
    form = '''
    <form action="/save_wine" method="post">
        <input type="text" name="name" placeholder="Name">
        <input type="text" name="region" placeholder="Region">
        <input type="text" name="grape" placeholder="Grape">
        <input type="number" name="acidity" placeholder="Acidity">
        <input type="number" name="sweetness" placeholder="Sweetness">
        <input type="number" name="body" placeholder="Body">
        <input type="number" name="tannins" placeholder="Tannins">
        <input type="text" name="type" placeholder="Type">
        <input type="number" name="fruity" placeholder="Fruity">
        <input type="number" name="funky" placeholder="Funky">
        <input type="number" name="price" placeholder="Price">
        <input type="submit" value="Save">
    </form>
    '''

    # Link to the CSS file
    styles = '<link rel="stylesheet" href="/static/styles.css">'

    # Return the styles and the form as HTML
    return styles + form

@app.post("/save_wine")
async def save_wine(name: str = Form(...), region: str = Form(...), grape: str = Form(...),
                    acidity: int = Form(...), sweetness: int = Form(...), body: int = Form(...),
                    tannins: int = Form(...), type: str = Form(...), fruity: int = Form(...),
                    funky: int = Form(...), price: float = Form(...)):
    # Create a new row from the form data
    new_row = {'name': name, 'region': region, 'grape': grape, 'acidity': acidity, 'sweetness': sweetness,
               'body': body, 'tannins': tannins, 'type': type, 'fruity': fruity, 'funky': funky, 'price': price}

    # Append the new row to the DataFrame
    global df
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

    # Save the DataFrame to the CSV file
    df.to_csv('wine.csv', index=False)

    # Redirect to the root
    return HTMLResponse('<script>window.location.href="/";</script>')

@app.post("/recommend_wine", response_class=HTMLResponse)
async def recommend_wine(wine_name: str = Form(...)):
    # Check if the wine exists in the DataFrame
    if wine_name not in df['name'].values:
        return '<p style="color: red;">Wine not found</p>'

    # Get the wine data
    wine_data = df[df['name'] == wine_name].iloc[0]

    # Calculate the absolute difference between the selected wine and all others for the specified fields
    diff = df[['acidity', 'sweetness', 'tannins', 'body', 'fruity', 'funky']].sub(wine_data[['acidity', 'sweetness', 'tannins', 'body', 'fruity', 'funky']].values).abs()

    # Calculate the relative difference for the price
    price_diff = (df['price'] - wine_data['price']).abs() / wine_data['price']

    # Get wines with maximum deviation of 1 in the specified fields and maximum deviation of 15% in the price
    similar_wines = df[(diff <= VALUE_DIFF).all(axis=1) & (price_diff <= PRICE_DIFF) & (df.quantity > 0)]

    # Format the similar wines as an HTML list
    output = '<ul class="output">'
    for wine in similar_wines['name'].values:
        output += f'<li>{wine}</li>'
    output += '</ul>'

    # Add a "Go Back" button
    button = '<button onclick="location.href=\'/\'" type="button">Go Back</button>'

    # Link to the CSS file
    styles = '<link rel="stylesheet" href="/static/styles.css">'

    # Return the styles, the output, and the button as HTML
    return styles + output + button
