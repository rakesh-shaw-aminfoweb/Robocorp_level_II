from robocorp.tasks import task
from robocorp import browser

from RPA.HTTP import HTTP
from RPA.Tables import Tables
from RPA.PDF import PDF
from RPA.Archive import Archive
from RPA.FileSystem import FileSystem

@task
def order_robots_from_RobotSpareBin():
    """
    Orders robots from RobotSpareBin Industries Inc.
    Saves the order HTML receipt as a PDF file.
    Saves the screenshot of the ordered robot.
    Embeds the screenshot of the robot to the PDF receipt.
    Creates ZIP archive of the receipts and the images.
    """

    open_robot_order_website()
    download_csv_file()
    orders = get_orders()

    for row in orders:
        close_annoying_modal()
        fill_the_form(row)
        store_receipt_as_pdf(str(row["Order number"]))

    # archive_receipts()


def open_robot_order_website():
    """Navigate to the given URL"""
    browser.goto(url="https://robotsparebinindustries.com/#/robot-order")


def download_csv_file():
    """Downloads csv file from the given URL"""
    http = HTTP()
    http.download(url="https://robotsparebinindustries.com/orders.csv", overwrite=True)

def get_orders():
    """Get the order data into a table"""
    orders = Tables().read_table_from_csv("orders.csv", columns=["Order number", "Head", "Body", "Legs","Address"])
    return orders

def close_annoying_modal():
    """Close the initial pop-up"""
    page = browser.page()
    page.click("button:text('OK')")

def fill_the_form(order):
    """Fills the order info and click 'Preview' and 'ORDER' button"""
    page = browser.page()

    page.select_option("#head", str(order["Head"]))
    page.click("#id-body-"+str(order["Body"]))
    # leg_id = page.get_attribute("label:text('3. Legs:')","for")
    # page.fill("input[id='"+ leg_id +"']", str(order["Legs"]))
    page.fill("input[placeholder='Enter the part number for the legs']", order['Legs'])
    page.fill("#address", str(order["Address"]))
    page.click("button:text('Preview')")

    while(page.query_selector("#receipt") is None):
        page.click("button:text('Order')")


def store_receipt_as_pdf(order_number):
    """Store the order receipt as a PDF file"""

    page = browser.page()
    pdf = PDF()
    lib = FileSystem()
    lib.create_directory("output/receipts")
    pdf_path = "output/receipts/order_"+order_number+".pdf"

    page.locator("#receipt").wait_for(state='attached')
    order_receipt_html = page.locator("#receipt").inner_html(timeout=10)
    pdf.html_to_pdf(order_receipt_html, pdf_path)
    screenshot_robot(order_number)
    embed_screenshot_to_receipt("output/receipts/"+order_number+".png", pdf_path)
    page.click("button:text('Order another robot')")
      
    
def screenshot_robot(order_number):
    """Take a screenshot of the page"""
    page = browser.page()
    page.locator(selector="#robot-preview-image").screenshot(path="output/receipts/"+order_number+".png")

def embed_screenshot_to_receipt(screenshot, pdf_file):
    """Embed the robot screenshot to the receipt PDF file"""

    list_of_files = [screenshot +':align=center']
    print("list_of_files: ",list_of_files)

    pdf = PDF()
    pdf.open_pdf(pdf_file)
    pdf.add_files_to_pdf(files=list_of_files,target_document=pdf_file,append=True)
    pdf.save_pdf(output_path=pdf_file)
    pdf.close_all_pdfs()

def archive_receipts():
    lib = Archive()
    lib.archive_folder_with_zip("output/receipts", "receipts.zip")

