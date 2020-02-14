#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

import os

from subprocess import getoutput
from py_obj_data_tools import PickleDataType, ExtendedDict, Extended_UniqueItem_List
from collections import Counter
from random import randint
from cli_tools import vermelho, azul_claro, branco, verde, verde_limao, verde_mar, verde_agua, verde_florescente, amarelo, rosa, cinza, salmao, select_op, select_ops
from itertools import cycle

cores = cycle([vermelho, azul_claro, verde, verde_limao, verde_florescente, amarelo, rosa, cinza, salmao])
cores_autores = cycle([verde, verde_florescente, verde_mar, verde_agua, amarelo])
cores_periodos = cycle([vermelho, rosa, salmao])

class NoteBook(PickleDataType):
    def __init__(self):
        super(NoteBook, self).__init__()
        self.id_notebook = input(verde("Qual o nome deste notebook?\n"))
        self.nfo = ExtendedDict()
        self.time_tags = Extended_UniqueItem_List()
        self.escopos = Extended_UniqueItem_List()
        self.assuntos = Extended_UniqueItem_List()
        self.autores = Extended_UniqueItem_List()
        self.end_interval_tag = Extended_UniqueItem_List()
        self.related_register_color = {}
        self.end_point = [' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ']
        self.start_point = [' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ']
        self.max_wid = 100
        self.line = ''
        self.persist()
        
    def _insert_tags(self, field, prompt):
        output = []
        while True:
            res = input(verde(prompt))
            output.append(res)
            print('')
            print(amarelo('Inserir outro marcador?'))
            op = select_op(['Sim', 'Não'], 1)
            if op == ["Não"]:
                break
        for item in output:
            field.append(item)
        return output

    def _add_text_field(self, prompt):
        output = input(verde(prompt))
        return output

    def _add_checklist(self, field, prompt):
        print('')
        print(verde(prompt))
        if len(field) == 0:
            output = self._insert_tags(field, prompt)
        else:
            op = select_ops(field + ['Outro'], 1)
            if op == ['Outro']:
                output = self._insert_tags(field, prompt)
            else:
                output = op
        return output

    def _add_multiline_text(self, prompt):
        print('')
        print(verde(prompt))
        op = select_op(['Sim', 'Não'], 1)
        if op == ['Sim']:
            tmp_fname = 'tmp_note_info_{}'.format(str(randint(0,1000)))
            os.system('nano /tmp/{}'.format(tmp_fname))
            output = getoutput('cat /tmp/{}'.format(tmp_fname))
        else:
            output = ''
        return output

    def _edit_text_field(self, field, prompt):
        print('')
        print(verde(prompt))
        input_value = input(amarelo("=> {}".format(field)))
        if not input_value:
            return field
        else:
            return input_value

    def _edit_checklist(self, field, prompt, reference_field):
        print('')
        print(verde(prompt))
        print(amarelo("=> {}".format(field)))
        input_value = select_ops(reference_field + ['Não alterar...'], 1)
        if input_value == ['Não alterar...']:
            return field
        else:
            return input_value

    def _edit_multiline_text(self, field):
        tmp_fname = 'tmp_note_info_{}'.format(str(randint(0,1000)))
        with open('/tmp/{}'.format(tmp_fname), 'w') as f:
            f.write(field)
        os.system('nano /tmp/{}'.format(tmp_fname))
        output = getoutput('cat /tmp/{}'.format(tmp_fname))
        return output

    def _print_multiline_string(self, s, indent_val=0):
        s = s.replace('\n', '\u255B')
        while True:
            if s.find('  ') != -1:
                s = s.replace('  ', ' ')
            if s.find('\u255B\u255B') != -1:
                s = s.replace('\u255B\u255B', '\u255B')
                s = s.replace('\u255B ', '\u255B')
                s = s.replace(' \u255B', '\u255B')
            else:
                break
        
        s = s.split('\u255B')
        output = []
        for paragraph in s:
            left_space = " " * indent_val 
            size = self.max_wid - (indent_val*2)
            idx_max = len(s)-1
            idx_init = 0
            idx_cut = int(size)
            while True:
                try:
                    if paragraph[idx_cut] == ' ':
                        output.append(left_space + paragraph[idx_init:idx_cut].strip('\n').strip().ljust(self.max_wid))
                        idx_max -= idx_cut
                        idx_init = int(idx_cut)
                        idx_cut = int(idx_init) + size
                    else:
                        idx_seek = -1
                        while True:
                            if paragraph[idx_cut+idx_seek] == ' ':
                                output.append(left_space + paragraph[idx_init:idx_cut+idx_seek].strip('\n').strip().ljust(self.max_wid))
                                idx_max -= idx_cut+idx_seek
                                idx_init = int(idx_cut+idx_seek)
                                idx_cut = int(idx_init) + size
                                break
                            else:
                                idx_seek -= 1
                except IndexError:
                    output.append(left_space + paragraph[idx_init:].strip('\n').strip().ljust(self.max_wid))
                    #output.append('\n'.ljust(self.max_wid))
                    break

        return output

    def _render_doc_info(self, filters, tag, doc, show_assunto, show_detalhes):
        if doc == None:
            print('Skiping')
            return

        if not filters:
            self._show_event_info(tag, doc, show_assunto, show_detalhes)
            return

        for filter_tag in filters:
            if filter_tag in doc['assunto'] or filter_tag in doc['escopo']:
                self._show_event_info(tag, doc, show_assunto, show_detalhes)
                break

    def _show_event_info(self, tag, doc, show_assunto, show_detalhes):
        current_color = ''
        assunto = ", ".join(doc['assunto'])
        escopo = ", ".join(doc['escopo'])
        topico = doc['topico']
        idx=None

       
        if doc['tipo'] == 'Período/intervalo':
            current_color = next(cores_periodos)

            #Procura por um Slot vazio no inicio da linha...
            idx = 0
            while True:
                if self.start_point[idx] == ' ':
                    self.start_point[idx] = next(map(current_color, ['\u2502']))
                    break
                else:
                   idx += 1

            end_date = tag.split('_')[1]
            self.related_register_color[tag] = current_color
            self.related_register_color[end_date] = (current_color, topico, doc['tipo'], idx)
            self.end_interval_tag.append(doc['intervalo'][1])
            init_data = doc['intervalo'][0]
            line = "{marker}{tag} »» {topico} ({escopo})".format(marker='', tag=init_data, topico=topico, escopo=escopo)
            self.line = next(map(current_color, [line]))
            
        elif doc['tipo'] == 'Autor':
            current_color = next(cores_autores)

            #Procura por um Slot vazio no final da linha...
            idx = -1
            while True:
                if self.end_point[idx] == ' ':
                    self.end_point[idx] = next(map(current_color, ['\u2502']))
                    break
                else:
                   idx -= 1

            self.related_register_color[tag] = current_color
            self.related_register_color[tag.split('_')[1]] = (current_color, topico, doc['tipo'], idx)
            self.end_interval_tag.append(doc['intervalo'][1])
            init_data = doc['intervalo'][0]
            line = "{marker}{tag} »» {topico} ({escopo})".format(marker='', tag=init_data, topico=topico, escopo=escopo)
            line_wid = len(line)
            complement_wid = self.max_wid - line_wid
            self.line = next(map(current_color, [line + ("\u2500" * complement_wid)]))

        elif doc['tipo'] == 'Referência':
            current_color = branco
            self.line = current_color("{marker}{tag} »» {topico} ({escopo})".format(marker='', tag=tag.split('-')[0], topico=topico, escopo=escopo))

        elif doc['tipo'] == 'Tese/ideia':
            current_color = azul_claro
            self.line = current_color("{marker}{tag} »» {topico} ({escopo})".format(marker='', tag=tag.split('-')[0], topico=topico, escopo=escopo))
        
        elif doc['tipo'] == 'Livro':
            current_color = rosa
            self.line = current_color("{marker} · {topico} ({tag}, {escopo})".format(marker='', tag=tag.split('-')[0], topico=topico, escopo=escopo))

        elif doc['tipo'] == 'Evento':
            current_color = branco
            self.line = "{marker}{tag} »» {topico} ({escopo})".format(marker='', tag=tag, topico=topico, escopo=escopo)

        self.print_notebook_line(topic_type=doc['tipo'], topic_color=current_color, line_nfo=self.line, current_idx=idx, end_of_block=False)

        if show_assunto:
            self.line = " » {assunto} «".format(assunto=assunto).ljust(self.max_wid+len(self.end_point))
            self.print_notebook_line(topic_color=rosa, line_nfo=self.line, current_idx=idx, end_of_block=False)

        if show_detalhes:
            lines = self._print_multiline_string(doc['detalhamento'])
            lines.append(' '.ljust(self.max_wid))
            for line in lines:
                self.line = next(map(cinza, [line]))
                self.print_notebook_line(topic_type='Detalhes', topic_color=current_color, line_nfo=self.line.ljust(self.max_wid), current_idx=idx, end_of_block=False)

    def _check_unused_slot_in_last_section(self, last_section, color, current_idx, end_of_block=False):
        columns = last_section.copy()

        for c in columns:
            if not end_of_block:
                if c == ' ' and columns.index(c) < current_idx:
                    columns[columns.index(c)] = next(map(color, ['\u2500']))
                elif columns.index(c) > current_idx and c.find('\u2500') != -1:
                    columns[columns.index(c)] = ' '
                
            else:
                if columns.index(c) > current_idx and c.find('\u2502') != -1 and c.find('\u2500') != -1:
                    columns[columns.index(c)] = ' '

        return columns

    def _check_unused_slot_in_first_section(self, first_section, color, current_idx, end_of_block=False):

        columns = first_section.copy()

        for c in columns:
            if not end_of_block:
                if c == ' ' and columns.index(c) > current_idx:
                    columns[columns.index(c)] = next(map(color, ['\u2500']))
                elif columns.index(c) < current_idx and c.find('\u2500') != -1:
                    columns[columns.index(c)] = ' '
                
            else:
                if columns.index(c) < current_idx and c.find('\u2502') != -1 and c.find('\u2500') != -1:
                    columns[columns.index(c)] = ' '

        return columns

    def print_notebook_line(self, topic_type=None, topic_color='', line_nfo='', current_idx=None, end_of_block=False):
        line_nfo = line_nfo.strip().ljust(self.max_wid)
        
        if current_idx != None and not end_of_block:
            if topic_type == 'Autor':
                self.end_point[current_idx] = next(map(topic_color, ['\u2510']))
                end_point_init = self.end_point[:current_idx]
                end_point_end = self.end_point[current_idx:]
                end_point_end = self._check_unused_slot_in_last_section(end_point_end, topic_color, current_idx, end_of_block)
                for c in end_point_init:
                    if c == ' ':
                        end_point_init[end_point_init.index(c)] =  next(map(topic_color, ['\u2500']))
                self.end_point = end_point_init + end_point_end
            
            elif topic_type == 'Período/intervalo':
                self.start_point[current_idx] = next(map(topic_color, ['\u250C']))
                start_point_init = self.start_point[:current_idx]
                start_point_end = self.start_point[current_idx:]
                start_point_init = self._check_unused_slot_in_first_section(start_point_init, topic_color, current_idx, end_of_block)
                for c in start_point_end:
                    if c == ' ':
                        start_point_end[start_point_end.index(c)] =  next(map(topic_color, ['\u2500']))
                self.start_point = start_point_init + start_point_end
        
        elif current_idx != None and end_of_block:
            if topic_type == 'Autor':
                self.end_point[current_idx] = next(map(topic_color, ['\u2518']))
                end_point_init = self.end_point[:current_idx]
                end_point_end = self.end_point[current_idx:]
                end_point_end = self._check_unused_slot_in_last_section(end_point_end, topic_color, end_of_block)
                for c in end_point_init:
                    if c == ' ':
                        end_point_init[end_point_init.index(c)] =  next(map(topic_color, ['\u2500']))
                self.end_point = end_point_init + end_point_end


            elif topic_type == 'Período/intervalo':
                self.start_point[current_idx] = next(map(topic_color, ['\u2514']))
                start_point_init = self.start_point[:current_idx]
                start_point_end = self.start_point[current_idx:]
                start_point_init = self._check_unused_slot_in_first_section(start_point_init, topic_color, current_idx, end_of_block)
                for c in start_point_end:
                    if c == ' ':
                        start_point_end[start_point_end.index(c)] =  next(map(topic_color, ['\u2500']))
                self.start_point = start_point_init + start_point_end


        first_section = ''.join(self.start_point)
        last_section = ''.join(self.end_point)

        '''
        if topic_type == 'Livro' or topic_type == 'Tese/ideia' or topic_type == 'Referência' or topic_type == 'Período/intervalo' or topic_type == 'Evento':
            #last_section = last_section.ljust(len(self.end_point))
            last_section = (" " * len(self.end_point)) + last_section.ljust(len(self.end_point))
            #last_section = (" " * len(self.end_point))
        '''

        if topic_type == 'Livro' or topic_type == 'Tese/ideia' or topic_type == 'Período/intervalo':# 
            last_section = (" " * len(self.end_point)) + last_section
        elif topic_type == 'Referência':
            last_section = (" " * 8) + last_section


        print(first_section + line_nfo.strip().ljust(self.max_wid) + last_section)

        #Limpando linhas...
        for c in self.end_point:
            if c.find('\u2500') != -1:
                self.end_point[self.end_point.index(c)] = ' '

        for c in self.start_point:
            if c.find('\u2500') != -1:
                self.start_point[self.start_point.index(c)] = ' '


        if current_idx != None and not end_of_block:
            if topic_type == 'Autor':
                self.end_point[current_idx] = next(map(topic_color, ['\u2502']))

            elif topic_type == 'Período/intervalo':
                self.start_point[current_idx] = next(map(topic_color, ['\u2502']))

        elif current_idx != None and end_of_block:
            if topic_type == 'Autor':
                self.end_point[current_idx] = next(map(topic_color, [' ']))
            
            elif topic_type == 'Período/intervalo':
                self.start_point[current_idx] = next(map(topic_color, [' ']))

    def add(self):
        tipo = select_op(['Autor', 'Período/intervalo', 'Referência', 'Tese/ideia', 'Evento', 'Livro'], 1)
        periodo = False

        if tipo == ['Evento']:
            topico = input(verde("Apresente o título resumido do evento:\n"))
            data_inicio = self._add_text_field("Ano/mês de início [AAAA/MM]:\n")
            ano = data_inicio.split('/')[0]
            mes = data_inicio.split('/')[1]

        if tipo == ['Livro']:
            topico = input(verde("Nome da obra a ser registrada:\n"))
            data_inicio = self._add_text_field("Ano de publicação [AAAA]:\n")
            ano = data_inicio
            mes = '00'


        elif tipo == ['Autor']:
            topico = input(verde("Nome do autor/a a ser registrado/a:\n"))
            data_inicio = self._add_text_field("Data de nascimento [AAAA/MM/DD]:\n")
            data_fim = self._add_text_field("Data de falecimento [AAAA/MM/DD]:\n")
            periodo = True
            intervalo = (data_inicio.replace('/','-'), data_fim.replace('/','-'))
            time_tag = data_inicio.replace('/','-') + '_' + data_fim.replace('/','-')
            self.time_tags.append(time_tag)

        elif tipo == ['Período/intervalo']:
            topico = input(verde("Indique um nome para o período ou evento de longo prazo:\n"))
            data_inicio = self._add_text_field("Ano/mês de início [AAAA/MM]:\n")
            data_fim = self._add_text_field("Ano/mês de fim [AAAA/MM]:\n")
            periodo = True
            intervalo = (data_inicio.replace('/','-'), data_fim.replace('/','-'))
            time_tag = data_inicio.replace('/','-') + '_' + data_fim.replace('/','-')
            self.time_tags.append(time_tag)
            
        elif tipo == ['Referência']:
            topico = input(verde("Indique a anotação de referência:\n"))
            ano = self._add_text_field("Ano de referencia:\n")
            mes = '00'

        elif tipo == ['Tese/ideia']:
            topico = input(verde("Apresente o título resumido que sintetise a ideia:\n"))
            ano = self._add_text_field("Ano de referencia:\n")
            mes = '00'

        escopo = self._add_checklist(self.escopos, "Indique um escopo/localidade e aperte enter:\n")
        assunto = self._add_checklist(self.assuntos, "Indique um assunto e aperte enter:\n")
        detalhamento = self._add_multiline_text("Inserir informações de detalhamento do evento/registro?")


        if not periodo:
            time_tag = str(ano)+'-'+str(mes).zfill(2)
            self.time_tags.append(time_tag)
            
        tmp = ExtendedDict()
        tmp[time_tag] = {}
        tmp[time_tag]['pendências'] = self._add_checklist(['Sim', 'Não'], "Ainda existem pendências para nota em questão?")
        tmp[time_tag]['tipo'] = tipo[0]
        if not periodo:
            tmp[time_tag]['ano'] = ano
            tmp[time_tag]['mes'] = mes
        else:
            tmp[time_tag]['intervalo'] = intervalo
        tmp[time_tag]['topico'] = topico
        tmp[time_tag]['detalhamento'] = detalhamento
        tmp[time_tag]['assunto'] = assunto
        tmp[time_tag]['escopo'] = escopo
        self.nfo = self.nfo + tmp
        self.repopulate_time_tags()
        self.persist()
    
    def merge_notebook(self, notebook):
        self.nfo = self.nfo + notebook.nfo
        for tag in notebook.time_tags:
            self.time_tags.append(tag)
        for escopo in notebook.escopos:
            self.escopos.append(escopo)
        for assunto in notebook.assuntos:
            self.assuntos.append(assunto)

    def show_events(self, filters=False, show_assunto=False, show_detalhes=False):
        for tag in self.time_tags:
            try:
                doc = self.nfo[tag]
                if type(doc) == list:
                    for doc_e in doc:
                        self._render_doc_info(filters, tag, doc_e, show_assunto, show_detalhes)
                else:
                    self._render_doc_info(filters, tag, doc, show_assunto, show_detalhes)
            except KeyError:

                topic_color = self.related_register_color[tag][0]
                topic_name = self.related_register_color[tag][1]
                topic_type = self.related_register_color[tag][2]
                column_slot_idx = self.related_register_color[tag][3]
                
                line = tag + " «« " + topic_name
                line_wid = len(line)
                complement_wid = self.max_wid - line_wid

                if topic_type == 'Autor':
                    self.line = next(map(topic_color, [line + ('\u2500' * complement_wid)]))
                
                elif topic_type == 'Período/intervalo':
                    self.start_point[column_slot_idx] = next(map(topic_color, ['%']))
                    self.line = next(map(topic_color, [line]))

                self.print_notebook_line(topic_color=topic_color, topic_type=topic_type, line_nfo=self.line, current_idx=column_slot_idx, end_of_block=True)

                if topic_type == 'Autor':
                    self.end_point[column_slot_idx] = ' '                
                
                elif topic_type == 'Período/intervalo':
                    self.start_point[column_slot_idx] = ' '

    def remove_event(self, time_tag):
        if self.nfo.get(time_tag) == None:
            delete_tags = []
            for k in self.nfo.keys():
                if k.find('_') != -1:
                    if k.split('_')[0] == time_tag:
                        delete_tags.append(k)

            for tag in delete_tags:
                del(self.nfo[tag])
                self.time_tags.remove(tag)                
        else:
            del(self.nfo[time_tag])
            self.time_tags.remove(time_tag)
        self.repopulate_time_tags()
        self.persist()


    def repopulate_time_tags(self):
        self.time_tags = Extended_UniqueItem_List()
        self.end_interval_tag = Extended_UniqueItem_List()
        for k in self.nfo.keys():
            self.time_tags.append(k)
            if k.find('_') != -1:
                self.time_tags.append(k.split('_')[1])
        self.persist()

    def edit_event(self, time_tag):
        doc = self.nfo[time_tag]
        if type(doc) == list:

            topicos = []
            topicos_doc_idx = []
            for doc_e in doc:
                topicos.append(doc_e['topico'])
                topicos_doc_idx.append(doc.index(doc_e))

            print(verde("Escolha qual tópico deverá ser editado:"))
            op = select_op(topicos, 1)[0]
            op_idx = topicos.index(op)
            
            doc[op_idx]['topico'] = self._edit_text_field(doc[op_idx]['topico'], "Apresente o tópico/evento ou informação resumida:")
            doc[op_idx]['escopo'] = self._edit_checklist(doc[op_idx]['escopo'], "Indique um escopo/localidade e aperte enter:", self.escopos)
            doc[op_idx]['assunto'] = self._edit_checklist(doc[op_idx]['assunto'], "Indique um assunto e aperte enter:", self.assuntos)
            doc[op_idx]['detalhamento'] = self._edit_multiline_text(doc[op_idx]['detalhamento'])

        else:
            doc['topico'] = self._edit_text_field(doc['topico'], "Apresente o tópico/evento ou informação resumida:")
            doc['escopo'] = self._add_checklist(self.escopos, "Indique um escopo/localidade e aperte enter:\n")
            doc['assunto'] = self._add_checklist(self.assuntos, "Indique um assunto e aperte enter:\n")
            doc['detalhamento'] = self._edit_multiline_text(doc['detalhamento'])
        
        self.persist()


