# -*- coding: utf-8 -*-
import json
import logging
import werkzeug

from datetime import date,datetime
from dateutil.relativedelta import relativedelta
from math import ceil

from odoo import fields, http, _
from odoo.addons.base.models.ir_ui_view import keep_query
from odoo.exceptions import UserError
from odoo.http import request, content_disposition
from odoo.tools import ustr

_logger = logging.getLogger(__name__)

from odoo.addons.survey.controllers.main import Survey

class CustomSurveyUser(Survey):

    @http.route('/survey/start/<string:survey_token>', type='http', auth='public', website=True)
    def survey_start(self, survey_token, answer_token=None, email=False, **post):
        """ Start a survey by providing
         * a token linked to a survey;
         * a token linked to an answer or generate a new token if access is allowed;
        """
        access_data = self._get_access_data(survey_token, answer_token, ensure_token=False)
        if access_data['validity_code'] is not True:
            return self._redirect_with_error(access_data, access_data['validity_code'])

        survey_sudo, answer_sudo = access_data['survey_sudo'], access_data['answer_sudo']
        if not answer_sudo:
            try:
                answer_sudo = survey_sudo._create_answer(user=request.env.user, email=email)
            except UserError:
                answer_sudo = False

        if not answer_sudo:
            try:
                survey_sudo.with_user(request.env.user).check_access_rights('read')
                survey_sudo.with_user(request.env.user).check_access_rule('read')
            except:
                return werkzeug.utils.redirect("/")
            else:
                return request.render("survey.403", {'survey': survey_sudo})

        # Select the right page
        if answer_sudo.state == 'new':  # Intro page
            route = 'photo' if survey_sudo.require_photo else 'fill' # Activate, you are beautiful ! <3
            data = {'survey': survey_sudo, 'answer': answer_sudo, 'page': 0,'route': route}
            if survey_sudo.date_start:
                if survey_sudo.date_start >= date.today():
                    return request.render('survey_score_template.survey_date', {'survey':survey_sudo})
                else:
                    return request.render('survey.survey_init', data)
            return request.render('survey.survey_init', data)
        else:
            return request.redirect('/survey/fill/%s/%s' % (survey_sudo.access_token, answer_sudo.token))

    # create view to take photo
    @http.route(['/survey/photo/<string:survey_token>/<string:answer_token>',
                 '/survey/photo/<string:survey_token>/<string:answer_token>'],
                type='http', auth='public', website=True)
    def take_photo(self, survey_token, answer_token, **post):
        access_data = self._get_access_data(survey_token, answer_token, ensure_token=False)
        survey_sudo, answer_sudo = access_data['survey_sudo'], access_data['answer_sudo']
        data = {'survey': survey_sudo, 'answer': answer_sudo}
        if answer_sudo.state == 'done':  # Display success message
            return request.render('survey.sfinished', self._prepare_survey_finished_values(survey_sudo, answer_sudo))
        else:
            return request.render('survey_take_photo.survey_photo', data)

    # # save photo
    @http.route(['/survey/photo/fill/<string:survey_token>/<string:answer_token>',
                 '/survey/photo/fill/<string:survey_token>/<string:answer_token>'],
                type='http', auth='public', website=True)
    def photo_fill(self, survey_token, answer_token, prev=None, **post):
        access_data = self._get_access_data(survey_token, answer_token, ensure_token=False)
        survey_sudo, answer_sudo = access_data['survey_sudo'], access_data['answer_sudo']
        if 'image' in post:
            image = post['image'].replace("data:image/jpeg;base64,", "") # replace prefix
            answer_sudo.write({'picture':image})
        if answer_sudo.state == 'done':  # Display success message
            return request.render('survey.sfinished', self._prepare_survey_finished_values(survey_sudo, answer_sudo))
        else:
            return request.redirect('/survey/fill/%s/%s' % (survey_sudo.access_token, answer_token))