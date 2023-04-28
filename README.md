# au-school-holiday-scraper
Web scraper which gathers school holiday data across a range of target years and states, and outputs it in a variety of useful csv formats.

---

## About

Gathers data from a network of state by state websites like https://www.nswschoolholiday.com.au/ which track school holidays across australia.

Iteratively accesses & transforms tables across these sites for a specified range of years and pool of target states.

Does this through the main `get_school_dates()` function.

---

## How to use

Clone the repo run the main function at the bottom of the `Main.py` script and customise the arguments as needed.

### get_school_dates() function

```Python
def get_school_dates(start_year,
                     end_year,
                     output_folder_target,
                     output_mode='startfinish',
                     targets=None,
                     show_qa_printouts=False,
                     drop_terms=True):
 ```
---

### Parameters

#### `start_year` type: int

The first year (inclusive) of the range of years you want data for.

#### `end_year` type: int

The last year (inclusive) of the range of years you want data for.

#### `output_folder_target` type: str

The absolute path of the folder you want to save csv data outputs to.

#### `output_mode` type: str

How you want to output the csv containing the data. See csv examples above.

Takes arguments:

- **'startfinish'** - Dates represented by start and finish dates
- **'dayrows'** - Each date and state combo between the start and finish represented in its own row
- **'binarydayrows'** - Each date between the start and finish represented in its own row, with states as columns with either 1 or 0 representing if that date has a school holiday on that date.

#### `targets` # type: list

Defaults to a list of all states, but can be set with any list of states like `['act','nsw','vic']`.

#### `show_qa_printouts` # type: bool

`False` by default. If set to `True` will print useful information to the command line as the script runs.

#### `drop_terms` # type: bool

`True` by default. If set to `False` rows representing the school terms won't be dropped from the output.
