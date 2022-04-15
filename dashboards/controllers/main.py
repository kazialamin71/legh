
from openerp.addons.web import http
from openerp.addons.web.http import request

class org_chart_dept(http.Controller):
    @http.route(["/hospital/chart/"], type='http', auth="public", website=True)
    def view(self, message=False, **post):
        values = {
        }
        return request.website.render('legh.hospital_chart', values)

