from django import forms 
import re

class RutForm(forms.Form):
    rut = forms.CharField( label="RUT",
                           max_length=12,
                           widget=forms.TextInput(attrs={'placeholder':'Ej: 12345678-9',
                                                         'class': 'form-control'}),
                          )
    
    def clean_rut(self):
        rut = self.cleaned_data['rut'].upper().replace(".","").replace("-","")
        if not re.match(r'^\d{7,8}[0-9K]$', rut):
            raise forms.ValidationError("Formato de RUT inválido.")
        
        rut_num = rut[:-1]
        dv = rut[-1]

        if not self.validar_dv(rut_num, dv):
            raise forms.ValidationError("RUT no válido.")
        
        return f"{rut_num}-{dv}"
    
    def validar_dv(self,rut,dv):
        reversed_digits = map(int, reversed(rut))
        factors = [2,3,4,5,6,7] * 2
        s = sum(d * f for d, f in zip(reversed_digits, factors))
        res = 11 - (s % 11)
        dv_calc = '0' if res == 11 else 'K' if res == 10 else str(res)
        return dv.upper() == dv_calc