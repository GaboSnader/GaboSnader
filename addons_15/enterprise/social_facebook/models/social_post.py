# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import requests

from odoo import api, models
from odoo.osv import expression
from werkzeug.urls import url_join


class SocialPostFacebook(models.Model):
    _inherit = 'social.post'

    @api.depends('live_post_ids.facebook_post_id')
    def _compute_stream_posts_count(self):
        super(SocialPostFacebook, self)._compute_stream_posts_count()

    def _get_stream_post_domain(self):
        domain = super(SocialPostFacebook, self)._get_stream_post_domain()
        facebook_post_ids = [facebook_post_id for facebook_post_id in self.live_post_ids.mapped('facebook_post_id') if facebook_post_id]
        if facebook_post_ids:
            return expression.OR([domain, [('facebook_post_id', 'in', facebook_post_ids)]])
        else:
            return domain

    def _format_images_facebook(self, facebook_account_id, facebook_access_token):
        self.ensure_one()

        formatted_images = []
        for image in self.image_ids:
            facebook_photo_endpoint_url = url_join(self.env['social.media']._FACEBOOK_ENDPOINT, '/v10.0/%s/photos' % facebook_account_id)

            post_result = requests.request('POST', facebook_photo_endpoint_url,
                params={
                    'published': 'false',
                    'access_token': facebook_access_token
                },
                files={'source': ('source', image.with_context(bin_size=False).raw, image.mimetype)},
                timeout=15
            )

            formatted_images.append({'media_fbid': post_result.json().get('id')})

        return formatted_images
