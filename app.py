from flask import Flask, render_template, request
import calc
from calc import calc_from_area, calc_from_budget, calc_from_capacity
import solar_roof
from solar_roof import output

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/overlay', methods=['GET', 'POST'])
def overlay():
    if request.method == 'POST':
        option = request.form.get('option')  # Assuming 'option' is a form field
        roof = request.files['rooffile']
        panel = int(request.form.get('solarpanel'))
        budget = int(request.form.get('budget'))
        state = request.form.get('state')
        category = request.form.get('category')
        cost = int(request.form.get('cost'))

        print(state)

        ans = []
        roofarea = 0

        if roof:
            roofarea = output(roof)
            ans = calc_from_area(state, roofarea, category, cost)
        elif panel:
            ans = calc_from_capacity(state, panel, category, cost)
        elif budget:
            ans = calc_from_budget(state, budget, category, cost)

        return render_template('overlay.html', state=state, rad=ans[0], electricity=ans[1], cap=ans[2],
                               cost_gst=ans[3], wosubsidy=ans[4], wsubsidy=ans[5], annual=ans[6], life=ans[7],
                               cost=cost, month=ans[8], annualcost=ans[9], lifecost=ans[10], break_even=ans[11])

if __name__ == '__main__':
    app.run(debug=True)
