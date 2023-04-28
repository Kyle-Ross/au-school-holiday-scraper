from urllib.parse import urljoin
from bs4 import BeautifulSoup
import pandas as pd
import requests
import pathlib
import re


# -------
# Function definition
# -------

def get_school_dates(start_year,
                     end_year,
                     output_folder_target,
                     output_mode='startfinish',
                     targets=None,
                     show_qa_printouts=False,
                     drop_terms=True):
    # -------
    # Set-up
    # -------

    # Setting print options for dataframe QA outputs
    pd.set_option('display.max_rows', None)
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)
    pd.set_option('display.colheader_justify', 'center')
    pd.set_option('display.precision', 2)

    # Define seperator string
    seperator = "\n_________________"

    # List of states, with url information and alternate url structures
    states_list = {'nsw':
                       {'url': 'https://www.nswschoolholiday.com.au/index.php/',
                        'subdir': 'nsw-school-holiday-dates-',
                        'min': 2015,
                        'altyears': {}
                        },
                   'qld':
                       {'url': 'https://www.qldschoolholiday.com.au/',
                        'subdir': 'queensland-school-holiday-dates-',
                        'min': 2014,
                        'altyears':
                            {2014: 'https://www.qldschoolholiday.com.au/qld-school-holiday-dates-2014/',
                             2015: 'https://www.qldschoolholiday.com.au/qld-school-holiday-dates-2015/',
                             2016: 'https://www.qldschoolholiday.com.au/qld-school-holiday-dates-2016/'}
                        },
                   'sa':
                       {'url': 'https://www.schoolholidayssa.com.au/',
                        'subdir': 'sa-school-holiday-dates-',
                        'min': 2015,
                        'altyears': {}
                        },
                   'vic':
                       {'url': 'https://www.victoriaschoolholidays.com.au/',
                        'subdir': 'vic-school-holiday-dates-',
                        'min': 2014,
                        'altyears':
                            {2014: 'https://www.victoriaschoolholidays.com.au/2014-term-dates',
                             2015: 'https://www.victoriaschoolholidays.com.au/2015-term-dates',
                             2016: 'https://www.victoriaschoolholidays.com.au/2016-term-dates'}
                        },
                   'wa':
                       {'url': 'https://www.schoolholidayswa.com.au/',
                        'subdir': 'wa-school-holiday-dates-',
                        'min': 2015,
                        'altyears': {}
                        },
                   'nt':
                       {'url': 'https://www.ntschoolholidays.com.au/',
                        'subdir': 'nt-school-holiday-dates-',
                        'min': 2018,
                        'altyears': {}
                        },
                   'act':
                       {'url': 'https://www.actschoolholidays.com.au/',
                        'subdir': 'act-school-holiday-dates-',
                        'min': 2018,
                        'altyears': {}
                        },
                   'tas':
                       {'url': 'https://tasmanianschoolholidays.com.au/',
                        'subdir': 'tasmanian-school-holiday-dates-',
                        'min': 2018,
                        'altyears': {2018: 'https://tasmanianschoolholidays.com.au/tas-school-holiday-dates-2018',
                                     2019: 'https://tasmanianschoolholidays.com.au/tas-school-holiday-dates-2019',
                                     2020: 'https://tasmanianschoolholidays.com.au/tas-school-holiday-dates-2020',
                                     2021: 'https://tasmanianschoolholidays.com.au/tas-school-holiday-dates-2021'}
                        }
                   }

    # Sets the default value for the targets argument
    if targets is None:
        targets = ['nsw', 'qld', 'sa', 'vic', 'wa', 'nt', 'act', 'tas']

    # List for storing dataframes
    df_list = []

    # List of dicts for storing missing data
    missing_list = []

    # List for storing dfs of removed rows
    removed_rows_list = []

    # Conditional printout for QA
    if show_qa_printouts:
        print(f'{"_" * 10}\n{"_" * 10}\nState Targets are {targets}{seperator * 2}')

    # ---------
    # Main Loop
    # ---------

    # Looping over target states
    for target_state in targets:

        # Conditional printout for QA
        if show_qa_printouts:
            print(f' {targets}')

        # Looping over years in range
        for year in range(start_year, end_year + 1):

            # Conditional printout for QA
            if show_qa_printouts:
                print(f'Year: {year}{seperator * 2}')

            # Checking if requested year is below the minimum
            if year < states_list[target_state]['min']:

                # Conditional printout for QA
                if show_qa_printouts:
                    print(f"{target_state.upper()} data not pulled for year {year}, '{states_list[target_state]['url']}' "
                          f"does not have data before {states_list[target_state]['min']}.")

                # Appending dict to list of missing data
                missing_list.append({'Type': 'below minimum available',
                                   'Source': 'dict lookup',
                                   'Year': year,
                                   'State': target_state.upper()})

                continue

            else:

                # Conditional printout for QA
                if show_qa_printouts:
                    print(f'{year} above minimum for {target_state} = True{seperator}')

            # ---------------------
            # Building URL to scrape
            # ---------------------

            # Checks for alternate URL types by year
            if year in states_list[target_state]['altyears']:
                url = states_list[target_state]['altyears'][year]

            # Otherwise uses the default url structure
            else:
                url = urljoin(states_list[target_state]['url'], states_list[target_state]['subdir'] + str(year))

            # Conditional printout for QA
            if show_qa_printouts:
                print(f'URL: {url}{seperator}')

            # ------------------------------------------------
            # Accessing HTML data & getting table as dataframe
            # ------------------------------------------------

            # Try except block to capture 404 errors
            try:
                # Send a GET request to the URL and store the response
                response = requests.get(url)

                # Raise an exception for 404 errors
                response.raise_for_status()

                # Create a BeautifulSoup object from the response content
                soup = BeautifulSoup(response.content, "html.parser")

                # Find the first table element on the page
                table = soup.find("table")

                # Extract the table data and store it in a list
                table_data = []
                for row in table.find_all("tr"):
                    row_data = []
                    for cell in row.find_all(["th", "td"]):
                        row_data.append(cell.get_text(strip=True))
                    table_data.append(row_data)

                # Convert the table data list to a pandas dataframe
                df = pd.DataFrame(table_data[1:], columns=table_data[0])

                # ----------------------
                # Processing NaN values
                # ----------------------

                # create a new DataFrame with rows containing NaN values for use in QA
                df_na = df[df.isna().any(axis=1)]

                # Removing any completely empty rows
                df_na = df_na.dropna(how='all')

                # Adding columns to df_na
                df_na.insert(0, 'State', target_state.upper())
                df_na.insert(0, 'Year', year)

                # Append that dataframe to removed_rows_list
                removed_rows_list.append(df_na)

                # Conditional printout for QA
                if show_qa_printouts:
                    print(f'Rows with NaNs that were removed:\n{df_na}{seperator}')

                # remove rows containing NaN values from the original DataFrame
                df = df.dropna()

                # -------------------------------
                # Data prep for page by page data
                # -------------------------------

                # Trim all column names
                df = df.rename(columns=lambda x: x.strip())

                # Drop length column
                df = df.drop(['Length'], axis=1)

                # Trimming all values in all string columns
                df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

                # Adding the year to the end of the 'Start' column if it isn't there
                df['Start'] = df['Start'].apply(
                    lambda x: x + f" {year}" if str(year) not in x else x)

                # Add identifier columns
                df['State'] = target_state.upper()
                df['Calendar_Year'] = year

                # Renaming Period column to School_Period
                df = df.rename(columns={'Period': 'School_Period_Name'})

                # Creating a field which describes the term type based on contained text
                df['School_Period_Type'] = df['School_Period_Name'].apply(
                    lambda x: 'Holiday' if 'Holiday' in x else ('Term' if 'Term' in x else 'Other'))

                # Adjusting column order
                df = df.reindex(
                    columns=['Calendar_Year', 'State', 'School_Period_Type', 'School_Period_Name', 'Start', 'Finish'])

                # Conditional printout for QA
                if show_qa_printouts:
                    print(f'Final dataframe: \n{df}{seperator}')

                # Add dataframe to list before looping
                df_list.append(df)

            # End point for 404 errors
            except requests.exceptions.HTTPError as e:

                # Conditional printout for QA
                if show_qa_printouts:
                    print(f"HTTP error: {e}{seperator}")

                # Adding dictionary values to missing data list
                missing_list.append({'Type': '404', 'Source': url, 'Year': year, 'State': target_state.upper()})

    # -------------------------------
    # Data prep for combined data
    # -------------------------------

    # Combining all dataframes
    combo_df = pd.concat(df_list)

    # Conditionally dropping terms column
    if drop_terms:
        combo_df = combo_df[combo_df["School_Period_Type"] == "Holiday"]

    # Removing characters to establish consistent formatting
    combo_df['Start'] = combo_df['Start']\
        .str.replace(',', '')\
        .str.replace('(tbc)', '')\
        .str.replace('(TBC)', '')\
        .str.replace('*', '')\
        .apply(lambda x: re.sub(r'(\d+)(st|nd|rd|th)', r'\1', x))

    combo_df['Finish'] = combo_df['Finish']\
        .str.replace(',', '')\
        .str.replace('(tbc)', '')\
        .str.replace('(TBC)', '')\
        .str.replace('*', '')\
        .apply(lambda x: re.sub(r'(\d+)(st|nd|rd|th)', r'\1', x))

    # Spot replacements for missing data
    combo_df.loc[combo_df['Start'] == 'Wednesday 21 December 2016', 'Finish'] = 'Tuesday 2 February 2021'

    # Trimming all values in all string columns
    combo_df = combo_df.applymap(lambda x: x.strip() if isinstance(x, str) else x)

    # Convert dates to date format
    combo_df['Start'] = pd.to_datetime(combo_df['Start'], format='%A %d %B %Y')
    combo_df['Finish'] = pd.to_datetime(combo_df['Finish'], format='%A %d %B %Y')

    # Sorting the combo dataframe
    combo_df = combo_df.sort_values(["State", "Start"])

    # ----------------------------------------------
    # Date transformation conditional on output_mode
    # ----------------------------------------------

    # Dates are shown with start and finish columns
    if output_mode == "startfinish":
        # Assign the desired df to the output
        output_df = combo_df

    # Splitting data to have one unique date and state per row
    # Excepts binarydayrows mode as this is build from the dayrows dataframe
    elif output_mode == "dayrows" or output_mode == "binarydayrows":

        # Create an empty dataframe with the required columns
        dayrows_df = pd.DataFrame(
            columns=['Calendar_Year', 'State', 'School_Period_Type', 'School_Period_Name', 'Date'])

        # Loop through each row in the combo_df
        for index, row in combo_df.iterrows():
            # Extract the start and finish dates for the current row
            start_date = row['Start']
            finish_date = row['Finish']

            # Generate a list of dates between start and finish (inclusive)
            date_range = pd.date_range(start_date, finish_date)

            # Create a new dataframe with the dates and other column values from the current row
            temp_df = pd.DataFrame({
                'Calendar_Year': [row['Calendar_Year']] * len(date_range),
                'State': [row['State']] * len(date_range),
                'School_Period_Type': [row['School_Period_Type']] * len(date_range),
                'School_Period_Name': [row['School_Period_Name']] * len(date_range),
                'Date': date_range
            })

            # Append the new dataframe to the empty dataframe
            dayrows_df = pd.concat([dayrows_df, temp_df])

        # Reset the index of the new dataframe
        dayrows_df = dayrows_df.reset_index(drop=True)

        if output_mode == "dayrows":
            # Sorting the dataframe
            dayrows_df = dayrows_df.sort_values(["State", "Date"])
            # Assign the dayrows_df to the output var
            output_df = dayrows_df

        # Otherwise use that same data to create the binary format
        # Groups data by date and represents states as columns with 1s and 0s
        elif output_mode == "binarydayrows":

            # unpivot data, and replace values with with a 1 or 0
            binarydayrows_df = dayrows_df.pivot_table(
                index=['Calendar_Year', 'School_Period_Type', 'Date'], columns='State',
                values='State', aggfunc=lambda x: 1).fillna(0).reset_index()
            # Drops the 'School_Period_Name' column

            # Converting all floats to integers
            float_cols = binarydayrows_df.select_dtypes(include=['float']).columns
            binarydayrows_df[float_cols] = binarydayrows_df[float_cols].astype(int)

            # Assign the binarydayrows_df to the output var
            output_df = binarydayrows_df

    # Message for invalid mode arguments
    else:
        print(f'Entered output mode ({output_mode}) is incorrect.')

    # --------------------
    # Outputting final df
    # --------------------

    # Generate the output file name
    output_filename = f"{output_folder_target}\\AU School Hols - Data - " \
                      f"{start_year}-{end_year} - {output_mode}.csv"

    # Conditional printout for QA
    if show_qa_printouts:
        print(f'Final dataframe: \n{output_df}{seperator}')

    # Saving the output to the specified folder
    output_df.to_csv(output_filename, index=False)

    # -----------------------------
    # Outputting df of missing data
    # -----------------------------

    # Generate the missing files output file name
    missing_filename = f"{output_folder_target}\\AU School Hols - Missing Data - " \
                       f"{start_year}-{end_year}.csv"

    # Converting error list to dataframe
    df_missing = pd.DataFrame(missing_list)

    # Conditional printout for QA
    if show_qa_printouts:
        print(f'Missing data: \n{df_missing}{seperator}')

    # Outputting df_missing to specified folder
    df_missing.to_csv(missing_filename, index=False)

    # -----------------------------
    # Outputting df of removed rows
    # -----------------------------

    # Combining the many rows dfs
    all_removed_rows_df = pd.concat(removed_rows_list)

    # Conditional printout for QA
    if show_qa_printouts:
        print(f'Missing rows: \n{all_removed_rows_df}{seperator}')

    # Generate the removed rows files output file name
    removed_rows_filename = f"{output_folder_target}\\AU School Hols - Removed Rows - " \
                            f"{start_year}-{end_year}.csv"

    # Outputting removed_rows_filename to specified folder
    all_removed_rows_df.to_csv(removed_rows_filename, index=False)

    # --------------------
    # End of function
    # --------------------


# --------------------
# Running the function
# --------------------

# Get path of this script for the output target
script_location = pathlib.Path(__file__).parent.resolve()

# Function call for Default Start-Finish Format
get_school_dates(2010,
                 2026,
                 output_mode='startfinish',
                 targets=['nsw', 'qld', 'sa', 'vic', 'wa', 'nt', 'act', 'tas'],
                 output_folder_target=script_location,
                 show_qa_printouts=True,
                 drop_terms=True)

# Function Call for Day Rows format
get_school_dates(2010,
                 2026,
                 output_mode='dayrows',
                 output_folder_target=script_location,
                 targets=['nsw', 'qld', 'sa', 'vic', 'wa', 'nt', 'act', 'tas'],
                 show_qa_printouts=True,
                 drop_terms=True)

# Function call for Binary Day Rows format
get_school_dates(2010,
                 2026,
                 output_mode='binarydayrows',
                 output_folder_target=script_location,
                 targets=['nsw', 'qld', 'sa', 'vic', 'wa', 'nt', 'act', 'tas'],
                 show_qa_printouts=True,
                 drop_terms=True)
