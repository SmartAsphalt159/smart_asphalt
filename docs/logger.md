Logging Documentation

### file: logger.py

## Class Sys_logger:
Used for all of the system logging needs of the smart asphalt documentation.

### Functions

#### __init__
&nbsp;&nbsp;&nbsp;&nbsp; Initialize the sys logger class by calling functions from python's native logger module. 

#### log_error
&nbsp;&nbsp;&nbsp;&nbsp; Log an error to the smart_aspahlt.log file.

#### log_warning
&nbsp;&nbsp;&nbsp;&nbsp; Log a warning to the smart_aspahlt.log file.

#### log_info
&nbsp;&nbsp;&nbsp;&nbsp; Log general information to the smart_aspahlt.log file.

#### log_debug
&nbsp;&nbsp;&nbsp;&nbsp; Log debug errors to the smart_aspahlt.log file.

## Class Data_logger

### Functions

#### __init__
&nbsp;&nbsp;&nbsp;&nbsp; Initialize the data logger through calls to panda's functions. 

#### get_log_name
&nbsp;&nbsp;&nbsp;&nbsp; Read the text file to see what number run this is. This is done so that mulitple log files can coexist in the same directory.

#### log_data
&nbsp;&nbsp;&nbsp;&nbsp; Open file and write log data to it. Either get new file name or append to the existing file.

#### format_data
&nbsp;&nbsp;&nbsp;&nbsp; Format raw data so that it can be appended to the file properly.

#### update_df
&nbsp;&nbsp;&nbsp;&nbsp; Append formatted data to the dataframe.

#### print_df
&nbsp;&nbsp;&nbsp;&nbsp; Print out the current rows in the dataframe.
