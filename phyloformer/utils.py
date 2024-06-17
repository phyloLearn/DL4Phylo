from re import sub, compile

"""
    Function that prints a value with the corresponding text.
"""
def println(txt, param):
    print(txt + "\n", param, "\n")


"""
    Function that splits the typing data into multiple files.
"""
def split_typing_data(input_file, output_prefix, number_of_files, lines_per_file):
    # Compile the regular expression
    pattern = compile(r'[a-zA-Z]+-\d+ [a-zA-Z]+')

    with open(input_file, 'r') as f:
        header = sub("\w*complex", "", next(f))

        for i in range(number_of_files):
            output_file = f"{output_prefix}_{i + 1}.txt"
            
            with open(output_file, 'w') as out:
                out.write(header)  # Write the header to each output file

                for _ in range(lines_per_file):
                    line = next(f, None)
                    if line is None:
                        break  # End of input file

                    line = pattern.sub("", line)
                    out.write(line)