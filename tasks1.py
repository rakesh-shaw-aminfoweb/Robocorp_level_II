from robocorp.tasks import task
from robocorp import browser
from RPA.HTTP import HTTP
from RPA.Excel.Files import Files
from RPA.PDF import PDF
from RPA.Tables import Tables

@task
def order_robots_from_RobotSpareBin():
    download_csv_file()
    open_robot_order_website()
    get_orders()

def download_csv_file():
    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)

def open_robot_order_website():
    browser.goto("https://robotsparebinindustries.com/#/robot-order")
    close_annoying_modal()

def close_annoying_modal():
    page = browser.page()
    page.click("button:text('OK')")

def get_orders():
    CSV=Tables()
    orders = CSV.read_table_from_csv("orders.csv", header=True)
    for order in orders:
        fill_the_form(order)

def fill_the_form(order):
    page = browser.page()
    page.select_option("#head", str(order["Head"]))
    page.check(f"#id-body-{order['Body']}")
    page.fill("input[placeholder='Enter the part number for the legs']", order['Legs'])
    page.fill("input[placeholder='Shipping address']", order['Address'])

    element = page.query_selector('div.alert.alert-danger')
    is_present = element is not None

    if is_present:
        page.click("#order")
        print("is_present true: ",is_present)
    else:
        page.click("#order")
        print("is_present false: ",is_present)

    page.wait_for_selector("#order-another", state="visible")
    page.click("#order-another", timeout=60000)
    close_annoying_modal()

# def ss_confirmation_page(order):
#     page = browser.page()
#     page.screenshot(path=f"output/ss/receipt_{order['Order number']}.png")


# <div class="alert alert-danger" role="alert">Server Out Of Ink Error</div>