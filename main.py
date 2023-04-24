
from pathlib import Path

from playwright.sync_api import Playwright, TimeoutError, sync_playwright

USER_EMAIL = ""
USER_PASSWORD = ""
STRAVA_EXPORT_PATH = "./Strava_export/"
ACTIVITIES_CSV = STRAVA_EXPORT_PATH + "activities.csv"


def get_track_name(gpx_file:str):
    """
    Opens a GPX file from Strava and returns the name of the activity.

    Args:
        gpx_file (str): The file path of the GPX file to be read.

    Returns:
        str: The name of the activity extracted from the GPX file.

    Note:
        This function assumes that the input GPX file is in the format used by Strava, where the activity name is
        enclosed in '<name>' tags. The function uses buffered reading to efficiently search for the '<name>' tag
        and extract the activity name. If the GPX file format is different, please update the function accordingly.
    """
    with open(gpx_file, buffering=1) as f:
        while "<name>" not in (line := f.readline()):
            pass # go to the next one
        # we found the name tag
        # the value is between the tags "  <name>Vélo du midi</name>"
        # at positions                   012345678         -87654321
        name = line[8:-8]
    return name

def get_track_name_and_file(csv_file_path: str):
    """
    Extracts the 'Name' and 'File' values from a CSV file where the 'Type' is equal to 'Vélo'.

    Args:
        csv_file_path (str): The file path of the CSV file to be read.

    Yields:
        tuple: A tuple containing the extracted 'Nom de l'activité' and 'Nom du fichier' values for
               each row in the CSV file where the 'Type' is equal to 'Vélo'.

    Example:
        >>> for Name, File in get_track_name_and_file("path/to/your/csv/file.csv"):
        ...     print(f"Name: {Name}, File: {File}")
        Name: Example Name 1, File: Example File 1
        Name: Example Name 2, File: Example File 2
        Name: Example Name 3, File: Example File 3

    Note:
        This function assumes that the input CSV file has the following column indices:
        - 'Nom de l'activité' column is at index 2
        - 'Nom du fichier' column is at index 12
        - 'Type d'activité' column is at index 3
        If the column indices in the CSV file are different, please update the function accordingly.
    """
    import csv

    # Open the CSV file
    with open(csv_file_path, "r") as csv_file:
        # Create a CSV reader
        reader = csv.reader(csv_file)

        # Skip the header row
        next(reader)

        # Iterate through the rows and extract rows where Type is equal to "Vélo"
        for row in reader:
            if row[3] == "Vélo":
                # Extract the desired values from the row
                Name = row[2]
                File = row[12]

                yield Name, File


def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://geovelo.app/en/sign-in/")

    # find the login form
    # weirdly, the page has two forms, and only the second one works
    page.get_by_placeholder("Email").first.click()
    page.get_by_placeholder("Email").last.click()
    page.get_by_placeholder("Email").last.fill(USER_EMAIL)
    page.get_by_placeholder("Email").last.press("Tab")
    page.get_by_placeholder("Password").last.fill(USER_PASSWORD)
    page.get_by_role("button", name="Sign In").last.click()

    previous_is_success = True
    # upload the GPX files
    for activity_name, file_path in get_track_name_and_file(ACTIVITIES_CSV):
        # Some entries in the CSV do not have a name, fill an example one if needed
        if activity_name == "":
            activity_name = "example track"

        # ensure the GPX file exists
        if Path(STRAVA_EXPORT_PATH + file_path).is_file():
            # If the previous file is uploaded succefully,
            # we are sent back to the main page, so we need to open the 'upload dialog' again.
            # otherwise, we stay on the 'upload' dialog
            if previous_is_success:
                page.get_by_role("button", name="GPX", exact=True).click()

            # The input tag is difficult to find with a standard locator, so we use the XPath
            page.locator("//html/body/div[2]/div[3]/div/div[1]/div[1]/input").set_input_files(STRAVA_EXPORT_PATH + file_path)
            # TODO replace the file input with the following ?
            # page.get_by_role("button", name="Choose a GPX").click()
            # page.on("filechooser", lambda file_chooser: file_chooser.set_files(STRAVA_EXPORT_PATH + file_path))
            page.get_by_label("Title *").click()
            page.get_by_label("Title *").fill(activity_name)
            page.get_by_role("button", name="Import").click()

            try:
                # The trip was successfully uploaded, close the confirmation
                page.get_by_role("button", name="Close").click(timeout=5000)
                previous_is_success = True

            except TimeoutError:
                # The 'close' button is not found,
                # it means that the GPX is already uploaded
                previous_is_success = False
                print(f"{file_path} has already been uploaded")
                continue

    # ---------------------
    print("Done !")
    context.close()
    browser.close()


if __name__ == "__main__":

    with sync_playwright() as playwright:
        run(playwright)
