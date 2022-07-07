# -*- coding: utf-8 -*-
import json
import logging
import werkzeug

from uuid import uuid4
from datetime import date,datetime
from dateutil.relativedelta import relativedelta
from math import ceil

from odoo import fields, http, _
from odoo.addons.base.models.ir_ui_view import keep_query
from odoo.exceptions import UserError
from odoo.http import request, content_disposition
from odoo.tools import ustr

from odoo.addons.survey.controllers.main import Survey 

_logger = logging.getLogger(__name__)

class CustomSurveyUserScore(Survey):

    # ------------------------------------------------------------
    # START NOM-35
    # ------------------------------------------------------------

    # call the nom
    @http.route('/survey/nom-35/', type='http', auth='user', website=True)
    def nom(self, **kw):
        survey = request.env['survey.survey'].sudo()
        return request.render('survey_score_template.survey_nom', {'survey': survey})

    # start the nom
    @http.route('/survey/nom-35/start/', type='http', auth='user', website=True)
    def nom_start(self, **kw):
        user = self._get_user()
        survey = request.env['survey_score_template.survey_employee'].sudo().search([('user_id','=',user.id)])
        if not survey:
            token = str(uuid4())
            survey.create({
                'user_id': user.id,
                'token': token,
                'state': 'terms'
            })
            url = '/survey/terms/%s/' % token
        else:
            token = survey.token
            if survey.state == 'draft':
                url = '/survey/terms/%s/' % token
            if survey.state == 'terms':
                url = '/survey/terms/%s/' % token
            elif survey.state == 'employee':
                url = '/survey/employee/%s/' % token
            elif survey.state == 'traumatic':
                url = '/survey/traumatic/%s/' % token
            elif survey.state == 'in_surveys':
                if not survey.survey:
                    continuity = request.env['survey_score_template.continuity'].sudo().search([('name','=','nom-35')],limit=1)
                    if continuity:
                        sequence = 1 if not survey.survey_answer else survey.survey_answer
                        survey = [b for v in continuity for b in v.surveys_ids if b.sequence == sequence]
                        url = survey[0].public_url
                else:
                    url = survey.survey.public_url
            elif survey.state == 'closed':
                url = '/survey/thanks/%s/' % token
        return werkzeug.utils.redirect(url)

    # call terms
    @http.route('/survey/terms/<string:token>/', type='http', auth='user', website=True)
    def terms(self, token ,**kw):
        survey = request.env['survey.survey'].sudo()
        data = {'survey': survey,'url':'/survey/terms/accept/%s/' % token}
        return request.render('survey_score_template.survey_terms', data)

    @http.route('/survey/terms/accept/<string:token>/', type='http', auth='user', website=True)
    def terms_accept(self, token ,**kw):
        survey = request.env['survey_score_template.survey_employee'].sudo().search([('token','=',token)])
        survey.sudo().write({'state':'employee'})
        url = '/survey/employee/%s/' % survey.token
        return werkzeug.utils.redirect(url)

    @http.route('/survey/employee/<string:token>/', type='http', auth='user', website=True)
    def employee(self, token , **kw):
        survey = request.env['survey.survey'].sudo()
        employee = self._get_employee()
        user = self._get_user()
        gender = '' if not employee else employee.gender
        age = 0 if not employee else self._get_age(employee.birthday) if employee.birthday else 0
        job_name = '' if not employee else employee.job_id.name
        job_id = '' if not employee else employee.job_id.id
        department_name = '' if not employee else employee.department_id.name
        department_id = '' if not employee else employee.department_id.id
        data = {
            'survey_number': str(user.id).zfill(10),
            'today': date.today().strftime("%d/%m/%Y"),
            'name':user.name,
            'sex': gender,
            'age': age,
            'job': job_name,
            'job_id': job_id,
            'department': department_name,
            'department_id': department_id,
            'url': '/survey/employee/fill/%s/' % token,
            'survey': survey
        }
        return request.render('survey_score_template.survey_employee', data)

    def _get_age(self,birthday):
        today = date.today()
        years = today.year - birthday.year
        if today.month < birthday.month or (today.month == birthday.month and today.day < birthday.day):
            years -= 1
        return years

    @http.route(['/survey/employee/fill/<string:token>/'],type='http', auth="user", website=True)
    def employee_fill(self, token, **post):
        survey = request.env['survey_score_template.survey_employee'].sudo().search([('token','=',token)])
        data = {
            'job_id' : post['job_id'] if post['job_id'] != '' else False,
            'department_id' : post['department_id'] if post['department_id'] != '' else False,
            'sex' : post['sex'],
            'year' : post['year'],
            'level_sf' : post['level-sf'] if 'level-sf' in post else '',
            'level_primary' : post['level-primary'] if 'level-primary' in post else '',
            'level_secondary' : post['level-secondary'] if 'level-secondary' in post else '',
            'level_preparatory' : post['level-preparatory'] if 'level-preparatory' in post else '',
            'level_technical' : post['level-technical'] if 'level-technical' in post else '',
            'level_degree' : post['level-degree'] if 'level-degree' in post else '',
            'level_mastery' : post['level-mastery'] if 'level-mastery' in post else '',
            'level_doctorate' : post['level-doctorate'] if 'level-doctorate' in post else '',
            'job_type' : post['job_type'],
            'contract_type' : post['contract_type'],
            'personal_type' : post['personal_type'],
            'jornal_type' : post['jornal_type'],
            'turn' : post['turn'],
            'experience_job' : post['experience_job'],
            'experience_work' : post['experience_work'],
            'state': 'traumatic'
        }
        survey.sudo().write(data)
        return werkzeug.utils.redirect('/survey/traumatic/%s/' % token)

    @http.route('/survey/traumatic/<string:token>/', type='http', auth='user', website=True)
    def traumatic(self, token,**kw):
        survey = request.env['survey.survey'].sudo()
        url = '/survey/traumatic/is/%s/' % token
        data = {'survey': survey,'url_traumatic': url,'url_not_traumatic':'/survey/thanks/%s' % token}
        return request.render('survey_score_template.survey_traumatic', data)

    @http.route('/survey/traumatic/is/<string:token>/', type='http', auth='user', website=True)
    def traumatic_is(self, token,**post):
        survey = request.env['survey.survey'].sudo()
        survey_employee = request.env['survey_score_template.survey_employee'].sudo().search([('token','=',token)])
        self.create_traumatic(post,survey_employee)
        continuity = request.env['survey_score_template.continuity'].sudo().search([('name','=','nom-35')])
        continuity = sorted((c for c in continuity.surveys_ids if c.sequence),key=lambda x: x.sequence)
        surveys_to_answer = len(continuity)
        if continuity:
            url = continuity[0].public_url if continuity else '/survey/nom-35/'
            survey_employee.sudo().write({'state':'in_surveys','survey':continuity[0].id,'survey_answer':1,'surveys_to_answer':surveys_to_answer})
            return werkzeug.utils.redirect(url)
        else:
            return request.render('survey_score_template.survey_error', {'survey':survey,'message':'No se encontro la configuración de continuidad. Por favor contacte al administrador'})

    def create_traumatic(self,post,survey_employee):
        traumatic = request.env['survey_score_template.survey_traumatic'].sudo()
        data = {
            'user_id': self._get_user().id,
            'question_1':True if post['s1-1'] == 'Si' else False,
            'question_2':True if post['s1-2'] == 'Si' else False,
            'question_3':True if post['s1-3'] == 'Si' else False,
            'question_4':True if post['s1-4'] == 'Si' else False,
            'question_5':True if post['s1-5'] == 'Si' else False,
            'question_6':True if post['s1-6'] == 'Si' else False,
            'question_7':True if post['s2-1'] == 'Si' else False,
            'question_8':True if post['s2-2'] == 'Si' else False,
            'question_9':True if post['s3-1'] == 'Si' else False,
            'question_10':True if post['s3-2'] == 'Si' else False,
            'question_11':True if post['s3-3'] == 'Si' else False,
            'question_12':True if post['s3-4'] == 'Si' else False,
            'question_13':True if post['s3-5'] == 'Si' else False,
            'question_14':True if post['s3-6'] == 'Si' else False,
            'question_15':True if post['s3-7'] == 'Si' else False,
            'question_16':True if post['s4-1'] == 'Si' else False,
            'question_17':True if post['s4-2'] == 'Si' else False,
            'question_18':True if post['s4-3'] == 'Si' else False,
            'question_19':True if post['s4-4'] == 'Si' else False,
            'question_20':True if post['s4-5'] == 'Si' else False
        }
        traumatic = traumatic.sudo().create(data)
        survey_employee.sudo().write({'traumatic':traumatic.id})

    @http.route('/survey/thanks/<string:token>/', type='http', auth='user', website=True)
    def thanks(self, token ,**kw):
        survey = request.env['survey.survey'].sudo()
        survey_employee = request.env['survey_score_template.survey_employee'].sudo().search([('token','=',token)])
        survey_employee.sudo().write({'state':'closed'})
        return request.render('survey_score_template.survey_thanks', {'survey':survey})

    def _get_user(self):
        return request.env['res.users'].sudo().browse(request.uid)

    def _get_employee(self):
        user = request.env['res.users'].sudo().browse(request.uid)
        employee = user.employee_ids
        if employee:
            return employee[0]
        else:
            return False

    # ------------------------------------------------------------
    # CONTINUITY NOM-35
    # ------------------------------------------------------------

    def _redirect_with_error(self, access_data, error_key):
        survey_sudo = access_data['survey_sudo']
        answer_sudo = access_data['answer_sudo']

        if error_key == 'survey_void' and access_data['can_answer']:
            return request.render("survey.survey_void", {'survey': survey_sudo, 'answer': answer_sudo})
        elif error_key == 'survey_closed' and access_data['can_answer']:
            return request.render("survey.survey_expired", {'survey': survey_sudo})
        elif error_key == 'survey_auth' and answer_sudo.token:
            if answer_sudo.partner_id and (answer_sudo.partner_id.user_ids or survey_sudo.users_can_signup):
                if answer_sudo.partner_id.user_ids:
                    answer_sudo.partner_id.signup_cancel()
                else:
                    answer_sudo.partner_id.signup_prepare(expiration=fields.Datetime.now() + relativedelta(days=1))
                redirect_url = answer_sudo.partner_id._get_signup_url_for_action(url='/survey/start/%s?answer_token=%s' % (survey_sudo.access_token, answer_sudo.token))[answer_sudo.partner_id.id]
            else:
                redirect_url = '/web/login?redirect=%s' % ('/survey/start/%s?answer_token=%s' % (survey_sudo.access_token, answer_sudo.token))
            return request.render("survey.auth_required", {'survey': survey_sudo, 'redirect_url': redirect_url})
        elif error_key == 'answer_deadline' and answer_sudo.token:
            return request.render("survey.survey_expired", {'survey': survey_sudo})
        elif error_key == 'answer_done' and answer_sudo.token:
            user = self._get_user()
            survey_employee = request.env['survey_score_template.survey_employee'].sudo().search([('user_id','=',user.id)])
            continuity = request.env['survey_score_template.continuity'].sudo().search([('name','=','nom-35')]).surveys_ids
            if continuity:
                if survey_employee.survey_answer == survey_employee.surveys_to_answer:
                    url = '/survey/thanks/%s' % survey_employee.token
                elif survey_employee.survey_answer < survey_employee.surveys_to_answer:
                    continuity = sorted((c for c in continuity if c.sequence),key=lambda x: x.sequence)
                    next = self._found_neighbor(continuity,survey_sudo.sequence)
                    survey_employee.write({'survey_answer': survey_employee.survey_answer + 1,'survey':next.id})
                    url = next.public_url if next != [] else ''
            else:
                url = '/'
            return werkzeug.utils.redirect(url)
        return werkzeug.utils.redirect("/")

    def _found_neighbor(self,continuity,pos):
        lst = []
        # generamos la lista
        for c in continuity:
            lst.append(c.sequence)
        lst = sorted(lst)
        """
        Se asume que lst es una lista ordenada
        de menor a mayor.
        """
        # índice de pos en la lista
        index = lst.index(pos)
        # si pos no es el último 
        if index != len(lst)-1:
        # un elemento después de pos
            new_lst = lst[index+1:]
            # Verificamos que exista dentro de la sequencia
            for n in continuity:
                # obtenemos el objeto
                if n.sequence == new_lst[0]:
                    next = n
                else:
                    next = []
            # retorna el objeto siguiente (aka encuesta) o una lista vacia
            return next
        # si pos es el último
        return []


    # ------------------------------------------------------------
    # COMPLETED SURVEY ROUTES
    # ------------------------------------------------------------

    @http.route('/survey/results/<model("survey.survey"):survey>', type='http', auth='user', website=True)
    def survey_report(self, survey, answer_token=None, **post):
        '''Display survey Results & Statistics for given survey.'''
        result_template = 'survey.result'
        current_filters = []
        filter_display_data = []
        filter_finish = False

        answers = survey.user_input_ids.filtered(lambda answer: answer.state != 'new' and not answer.test_entry)
        if 'finished' in post:
            post.pop('finished')
            filter_finish = True
        if post or filter_finish:
            filter_data = self._get_filter_data(post)
            current_filters = survey.filter_input_ids(filter_data, filter_finish)
            filter_display_data = survey.get_filter_display_data(filter_data)
        return request.render(result_template,
                                      {'survey': survey,
                                       'answers': answers,
                                       'survey_dict': self._prepare_result_dict(survey, current_filters),
                                       'page_range': self.page_range,
                                       'current_filters': current_filters,
                                       'filter_display_data': filter_display_data,
                                       'filter_finish': filter_finish,
                                       'score': self._get_score(survey)
                                       })

    def _get_score(self,survey):
        survey_surveys = request.env['survey.user_input'].search([
            ('survey_id','=',survey.id),
            ('state','=','done')
        ])
        survey_len = len(survey_surveys)
        results = self.create_dictionary_score(survey_surveys,survey_len,survey)
        return results

    @http.route('/survey/print/<string:survey_token>', type='http', auth='public', website=True, sitemap=False)
    def survey_print(self, survey_token, review=False, answer_token=None, **post):
        '''Display an survey in printable view; if <answer_token> is set, it will
        grab the answers of the user_input_id that has <answer_token>.'''
        access_data = self._get_access_data(survey_token, answer_token, ensure_token=False)
        if access_data['validity_code'] is not True and (
                access_data['has_survey_access'] or
                access_data['validity_code'] not in ['token_required', 'survey_closed', 'survey_void', 'answer_done']):
            return self._redirect_with_error(access_data, access_data['validity_code'])

        survey_sudo, answer_sudo = access_data['survey_sudo'], access_data['answer_sudo']

        if survey_sudo.scoring_type == 'scoring_without_answers':
            return request.render("survey.403", {'survey': survey_sudo})

        return request.render('survey.survey_print', {
            'review': review,
            'survey': survey_sudo,
            'answer': answer_sudo,
            'page_nr': 0,
            'score': self.create_dictionary_score(answer_sudo,1,survey_sudo),
            'quizz_correction': survey_sudo.scoring_type != 'scoring_without_answers' and answer_sudo})

    def create_dictionary_score(self,survey_surveys,survey_len,survey):
        results = []
        category_list = []
        domain_list = []
        dimension_list = []
        answer_list = []
        total_score = {}
        score = 0
        for surveys in survey_surveys:
            # answers
            answers = surveys.user_input_line_ids
            score += surveys.quizz_score
            for answer in answers:
                # crear dictionarys
                answer_dict = dict()
                answer_dict['category'] = answer.value_suggested_row.category_id
                answer_dict['domain'] = answer.value_suggested_row.domain_id
                answer_dict['dimension'] = answer.value_suggested_row.dimension_id
                answer_dict['result'] = answer.answer_score
                # lists
                category_list.append(answer_dict['category'])
                domain_list.append(answer_dict['domain'])
                dimension_list.append(answer_dict['dimension'])
                answer_list.append(answer_dict)
        # delete for set
        category_list = list(set(category_list))
        domain_list = list(set(domain_list))
        dimension_list = list(set(dimension_list))
        # final
        category = self.get_results(category_list,'category',answer_list,survey_len)
        domain = self.get_results(domain_list,'domain',answer_list,survey_len)
        dimension = self.get_results(dimension_list,'dimension',answer_list,survey_len)
        if survey.qualification_id:
            total_score = self.final_score(survey,score,survey_len)
        # crear dicccionario final
        results.append({"category":category,"domain":domain,"dimension":dimension,"total_score":total_score})
        result = self.get_level(results)
        return result

    def final_score(self,survey,total,survey_len):
        score = {}
        qualification = survey.qualification_id
        try:
            total_score = (total / survey_len)
        except ZeroDivisionError:
            total_score = float(0)
        level = self.determine_score(
            qualification.null,
            qualification.low,
            qualification.medium,
            qualification.high,
            qualification.very_high,
            total_score)
        score = {
            'name': survey.qualification_id.name,
            'total': round(total_score,2),
            'level': level
        }
        return score

    # get result by taxonomy_list (category,domain,dimension)
    def get_results(self,taxonomy_list, taxonomy_str, answer_list, survey_len):
        results = []
        # total = sum(filtered_results)/survey_len
        for taxonomy in taxonomy_list:
            if taxonomy:
                filtered_results = [a['result']
                                    for a
                                    in answer_list
                                    if a[taxonomy_str] == taxonomy]
                try:
                    total = sum(filtered_results)/survey_len
                except ZeroDivisionError:
                    total = float(0)
                results.append({
                    "name":taxonomy.name,
                    "total":round(total,2),
                    "null":taxonomy.null,
                    "low":taxonomy.low,
                    "medium":taxonomy.medium,
                    "high":taxonomy.high,
                    "very_high":taxonomy.very_high,
                    "level": ''
                })
        return results

    def get_level(self,results):
        for r in results:
            for c in r['category']:
                c['level'] = self.determine_score(c['null'],c['low'],c['medium'],c['high'],c['very_high'],c['total'])
            for d in r['domain']:
                d['level'] = self.determine_score(d['null'],d['low'],d['medium'],d['high'],d['very_high'],d['total'])
            for di in r['dimension']:
                di['level'] = self.determine_score(di['null'],di['low'],di['medium'],di['high'],di['very_high'],di['total'])
        return r

    def determine_score(self,null,low,medium,hight,very_high,score):
        class_score = ''
        if score < null:
            class_score = "bg-dark" # "Nulo o despreciable"
        elif null <= score < low:
            class_score = "bg-success" # "Bajo"
        elif low <= score < medium:
            class_score = "bg-info" # "Medio"
        elif medium <= score < hight:
            class_score = "bg-warning" # "Alto"
        elif score > very_high:
            class_score = "bg-danger" # "Muy alto"
        return class_score