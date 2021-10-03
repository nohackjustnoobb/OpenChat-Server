from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class ServerInfoView(APIView):
    def get(self, request):
        serverInfoDict = {
            'serverName': 'Development Server',
            'serverType': 'Django',
            'serverVersion': 'Beta'
        }
        return Response(serverInfoDict, status=status.HTTP_200_OK)
