import json
from channels.generic.websocket import AsyncWebsocketConsumer

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        await self.send(text_data=json.dumps({
            "message": "✅ Connexion WebSocket établie avec succès !"
        }))

    async def disconnect(self, close_code):
        print(f" WebSocket déconnecté, code : {close_code}")

    async def receive(self, text_data):
        if not text_data:  # Vérifier si le message est vide
            await self.send(text_data=json.dumps({"error": "Message vide reçu"}))
            return

        try:
            data = json.loads(text_data)  # Décoder JSON
            message = data.get("message", "Aucun message reçu")
            
            # Envoyer le message en retour
            await self.send(text_data=json.dumps({
                "message": f"📩 Message reçu : {message}"
            }))
        
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({"error": "Format JSON invalide"}))

