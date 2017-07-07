import json

import httplib2
from braces import views
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse_lazy
from django.views import generic

from treccoreweb.search import helpers
from treccoreweb.search.logging_messages import LOGGING_MESSAGES as SEARCH_LOGGING_MESSAGES
from treccoreweb.interfaces.SearchEngine import functions as SearchEngine
from treccoreweb.interfaces.DocumentSnippetEngine import functions as DocEngine

import logging
logger = logging.getLogger(__name__)


class SearchHomePageView(views.LoginRequiredMixin, generic.TemplateView):
    template_name = 'search/search.html'

    def get(self, request, *args, **kwargs):
        # TODO: If we're not going to use electron.js, make sure the view
        # is only allowed to people with permission to access this page
        current_task = self.request.user.current_task
        if current_task.is_time_past():
            return HttpResponseRedirect(reverse_lazy('progress:completed'))

        if not current_task.setting.show_search:
            return HttpResponseRedirect(reverse_lazy('progress:home'))

        return super(SearchHomePageView, self).get(self, request, *args, **kwargs)


class SearchVisitAJAXView(views.CsrfExemptMixin, views.LoginRequiredMixin,
                       views.JsonRequestResponseMixin,
                       generic.View):
    require_json = False

    def post(self, request, *args, **kwargs):
        try:
            client_time = self.request_json.get(u"client_time")
            page_title = self.request_json.get(u"page_title")
        except KeyError:
            error_dict = {u"message": u"your input must include client_time, page title."}
            return self.render_bad_request_response(error_dict)

        log_body = {
            "user": self.request.user.username,
            "client_time": client_time,
            "result": {
                "message": SEARCH_LOGGING_MESSAGES.get("visit", None),
                "page_visit": True,
                "page_file": "search.html",
                "page_title": page_title
            }
        }
        logger.info("[{}]".format(log_body))

        context = {u"message": u"Your visit has been recorded."}
        return self.render_json_response(context)


class SearchInputStatusAJAXView(views.CsrfExemptMixin, views.LoginRequiredMixin,
                       views.JsonRequestResponseMixin,
                       generic.View):
    require_json = False

    def post(self, request, *args, **kwargs):
        try:
            client_time = self.request_json.get(u"client_time")
            isFocused = self.request_json.get(u"isFocused")
            page_title = self.request_json.get(u"page_title")
            search_bar_value = self.request_json.get(u"search_bar_value")
        except KeyError:
            error_dict = {u"message": u"your input must include client_time, page_title"
                                      u"search bar value, and isFocused."}
            return self.render_bad_request_response(error_dict)

        log_body = {
            "user": self.request.user.username,
            "client_time": client_time,
            "result": {
                "message": SEARCH_LOGGING_MESSAGES.get("search_input", None),
                "isFocused": isFocused,
                "search_bar_value": search_bar_value,
                "page_title": page_title
            }
        }
        logger.info("[{}]".format(log_body))

        context = {u"message": u"Your search input event has been recorded."}
        return self.render_json_response(context)


class SearchKeystrokeAJAXView(views.CsrfExemptMixin, views.LoginRequiredMixin,
                       views.JsonRequestResponseMixin,
                       generic.View):
    require_json = False

    def post(self, request, *args, **kwargs):
        try:
            client_time = self.request_json.get(u"client_time")
            page_title = self.request_json.get(u"page_title")
            character = self.request_json.get(u"character")
            isSearchbarFocused = self.request_json.get(u"isSearchbarFocused")
            search_bar_value = self.request_json.get(u"search_bar_value")
        except KeyError:
            error_dict = {u"message": u"your input must include client_time,"
                                      u" page title, character, isSearchbarFocused,"
                                      u" and search bar value."}
            return self.render_bad_request_response(error_dict)

        log_body = {
            "user": self.request.user.username,
            "client_time": client_time,
            "result": {
                "message": SEARCH_LOGGING_MESSAGES.get("keystroke", None),
                "character": character,
                "search_bar_value": search_bar_value,
                "isSearchbarFocused": isSearchbarFocused,
                "page_title": page_title
            }
        }
        logger.info("[{}]".format(log_body))

        context = {u"message": u"Your visit has been recorded."}
        return self.render_json_response(context)


class FindKeystrokeAJAXView(views.CsrfExemptMixin, views.LoginRequiredMixin,
                       views.JsonRequestResponseMixin,
                       generic.View):
    require_json = False

    def post(self, request, *args, **kwargs):
        try:
            client_time = self.request_json.get(u"client_time")
            doc_id = self.request_json.get(u"doc_id")
            page_title = self.request_json.get(u"page_title")
            character = self.request_json.get(u"character")
            isSearchbarFocused = self.request_json.get(u"isSearchbarFocused")
            search_bar_value = self.request_json.get(u"search_bar_value")
        except KeyError:
            error_dict = {u"message": u"your input must include client_time,"
                                      u" doc_id, character, isSearchbarFocused,"
                                      u" page_title and search bar value."}
            return self.render_bad_request_response(error_dict)

        log_body = {
            "user": self.request.user.username,
            "client_time": client_time,
            "result": {
                "message": SEARCH_LOGGING_MESSAGES.get("find_keystroke", None),
                "character": character,
                "search_bar_value": search_bar_value,
                "isSearchbarFocused": isSearchbarFocused,
                'page_title': page_title,
                "doc_id": doc_id
            }
        }
        logger.info("[{}]".format(log_body))

        context = {u"message": u"Your visit has been recorded."}
        return self.render_json_response(context)

class SearchListView(views.CsrfExemptMixin, generic.base.View):
    template = 'search/search_list.html'

    def post(self, request, *args, **kwargs):
        template = loader.get_template(self.template)
        try:
            search_input = request.POST.get("search_input")
            numdisplay = request.POST.get("numdisplay", 10)
        except KeyError:
            rendered_template = template.render({})
            return HttpResponse(rendered_template, content_type='text/html')
        context = {}
        documents_values, document_ids = None, None
        try:
            documents_values, document_ids, total_time = SearchEngine.get_documents(
                                                            search_input,
                                                            numdisplay=numdisplay
                                                         )
        except (TimeoutError, httplib2.HttpLib2Error):
            context['error'] = "Error happened. Please check search server."

        if document_ids:
            document_ids = helpers.padder(document_ids)
            documents_values = helpers.join_judgments(documents_values, document_ids,
                                                      self.request.user,
                                                      self.request.user.current_task)
        context["documents"] = documents_values
        context["query"] = search_input
        if total_time:
            context["total_time"] = "{0:.2f}".format(round(float(total_time), 2))

        rendered_template = template.render(context)
        return HttpResponse(rendered_template, content_type='text/html')


class SearchGetDocAJAXView(views.CsrfExemptMixin, views.LoginRequiredMixin,
                          views.JsonRequestResponseMixin,
                          views.AjaxResponseMixin, generic.View):

    require_json = False

    def render_timeout_request_response(self, error_dict=None):
        if error_dict is None:
            error_dict = self.error_response_dict
        json_context = json.dumps(
            error_dict,
            cls=self.json_encoder_class,
            **self.get_json_dumps_kwargs()
        ).encode('utf-8')
        return HttpResponse(
            json_context, content_type=self.get_content_type(), status=502)

    def get_ajax(self, request, *args, **kwargs):
        docid = request.GET.get('docid')
        query = request.GET.get('query')
        if not docid:
            return self.render_json_response([])
        try:
            document = DocEngine.get_documents([docid], query)
        except TimeoutError:
            error_dict = {u"message": u"Timeout error. Please check status of servers."}
            return self.render_timeout_request_response(error_dict)

        return self.render_json_response(document)
