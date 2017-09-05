class ExperimentsFormulas:
    code_dict = {0: "No experiment", 1:"ADCS Detumbling", 2: "Erase Flash", 3: "SunS", 4: "LEOP", 5: "RadFET", 6: "SADS", 7: "Sail", 8:"Fibonacci"}    

    @staticmethod
    def code(self, x):
        return code_dict[x]

    @staticmetod
    def result(self, x):
        return x

    @staticmethod
    def status(self, x):
        return x


experiments_formulas = {'Current experiment code': ExperimentsFormulas.code,
                        'Experiment Startup Result': ExperimentsFormulas.result,
                        'Last Experiment Iteration Status': ExperimentsFormulas.status}
