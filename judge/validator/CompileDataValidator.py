class CompileDataVaildator:
    '''
    Class to validate compile data.
    '''
    def validateCompileData(self , data):
        '''
        This function validates the data and returns isValid and errors.
        language - validates if language is present.
        code - validate if code is present and not empty.
        ignoreWarning - False if the string contains false (not case sensitive).
                        default True
        timeout - Timeout for the compilation process.
                  default 2

        @return (isValid , errors) tuple - Returns a tuple containing isValid and errors
                isValid bool - True if the given data is valid and can be compiled
                errors dict - A dictionary containing all the errors
        '''
        isValid = True
        errors = {}
        
        if not data:
            data = {}
            
        # Validate language
        if 'language' not in data:
            isValid = False
            errors['language'] = 'Language is required'
        
        #Validate code
        if 'code' not in data:
            isValid = False
            errors['code'] = 'Code is required'
        elif data['code'].strip() == '':
            isValid = False
            errors['code'] = 'Code must not be empty'
        else:
            data['code'] = data['code'].strip()
        
        #Validate ignoreWarnings
        if 'ignoreWarnings' not in data:
            data['ignoreWarnings'] = True
        else:
            if data['ignoreWarnings'].lower() == 'false':
                data['ignoreWarnings'] = False
            else:
                data['ignoreWarnings'] = True

        #Validate timeout
        if 'timeout' not in data:
            data['timeout'] = 2
        else:
            if not data['timeout'].isdigit():
                isValid = False
                errors['timeout'] = 'Timeout must be a positive integer'
            else:
                data['timeout'] = int(data['timeout'])

        return (isValid , errors)

        