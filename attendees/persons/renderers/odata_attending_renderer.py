from rest_framework.renderers import JSONRenderer


class ODataRenderer(JSONRenderer):

    def render(self, data, accepted_media_type=None, renderer_context=None):
        status_code = renderer_context['response'].status_code
        response = {
          "status": "success",
          "code": status_code,
          "data": data,
          "message": None
        }

        if str(status_code).startswith('2'):
            meta_dict = getattr(renderer_context.get('view').get_serializer().Meta, 'meta_dict')
            response["totalCount"] = meta_dict['total_count']
        else:
            response["status"] = "error"
            response["data"] = []
            try:
                response["message"] = data["detail"]
            except KeyError:
                response["data"] = data

        return super(ODataRenderer, self).render(response, accepted_media_type, renderer_context)


