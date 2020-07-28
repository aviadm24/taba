#!/usr/bin/env python
# -*- coding: utf-8 -*-



def translate(string):
    empty_string= ''
    for char in string:
        if char == 'א' :
            empty_string+= 'A'
        if char == 'ב' :
            empty_string += 'B'
        if char == 'ג':
            empty_string += 'G'
        if char == 'ד':
            empty_string += 'D'
        if char == 'ה':
            empty_string += 'H'
        if char == 'ו':
            empty_string += 'V'
        if char == 'ז':
            empty_string += 'Z'
        if char == 'ח':
            empty_string += 'HT'
        if char == 'ט':
            empty_string += 'T'
        if char == 'י':
            empty_string += 'I'
        if char == 'כ':
            empty_string += 'CH'
        if char == 'ל':
            empty_string += 'L'
        if char == 'מ':
            empty_string += 'M'
        if char == 'נ':
            empty_string += 'N'
        if char == 'ס':
            empty_string += 'S'
        if char == 'ע':
            empty_string += 'AA'
        if char == 'פ':
            empty_string += 'P'
        if char == 'צ':
            empty_string += 'Z'
        if char == 'ק':
            empty_string += 'K'
        if char == 'ר':
            empty_string += 'R'
        if char == 'ש':
            empty_string += 'SH'
        if char == 'ת':
            empty_string += 'T'
        if char== '-':
            empty_string+='-'
        if char=='/':
            empty_string+='-'
        else:
            try :
                num= int(char)
                empty_string+=char
            except:
                pass
    return (empty_string)


def google_translate(string):
    from googletrans import Translator

    translator = Translator()
    empty = ''
    for char in string:
        try:
            trans1 = translator.translate(char, dest='en')
            empty+=trans1.text
        except:
            empty+=trans1.text

    return(empty)
#if __name__=='__main__' :


