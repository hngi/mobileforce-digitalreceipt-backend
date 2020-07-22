from django.shortcuts import render
from .models import Promotions
from .serializers import PromotionSerializer
from rest_framework import status
from rest_framework.decorators import api_view
from django.http import JsonResponse



@api_view(["POST"])
def create_promotion(request):
    if request.method == "POST":

        if "image_url" not in request.data:
            return JsonResponse(
                {"error": "Enter the image_url"}, status=status.HTTP_400_BAD_REQUEST
            )
        if "text" not in request.data:
            return JsonResponse(
                {"error": "Enter the text"}, status=status.HTTP_400_BAD_REQUEST
            )
        if "link" not in request.data:
            return JsonResponse(
                {"error": "Enter the link"}, status=status.HTTP_400_BAD_REQUEST
            )

        data = {
            "imageUrl": request.data["image_url"],
            "text": request.data["text"],
            "link": request.data["link"],
        }
        serializer = PromotionSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=status.HTTP_200_OK)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["DELETE"])
def delete_promotion(request, id):
    if request.method == "DELETE":
        try:
            promotion = Promotions.objects.filter(id=id)
            if len(Promotions) == 0:
                return JsonResponse(
                    {"errors": "Promotion does not exitst"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            else:
                promotion.delete()
                return JsonResponse(
                    {"data": "Promotion deleted successfully"},
                    status=status.HTTP_200_OK,
                )
        except:
            pass


@api_view(["PUT"])
def update_promotion(request, id):
    if request.method == "PUT":
        try:
            if "promotion_id" not in request.data:
                return JsonResponse(
                    {"error": "Enter Promotion id"}, status=status.HTTP_400_BAD_REQUEST
                )

            promotionId = request.data["promotion_id"]

            promotion = Promotions.objects.get(id=promotionId)

            promotion.imageUrl = request.data["imageUrl"]
            promotion.text = request.data["text"]
            promotion.link = request.data["link"]
            promotion.save()
            updatePromotion = PromotionSerializer(promotion)
            return JsonResponse({"data": updatePromotion}, status=status.HTTP_200_OK)

        except Promotions.DoesNotExist:
            return JsonResponse(
                {"error": "No promotion was found with this id"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except Exception as error:
            return JsonResponse({"error": error}, status=status.HTTP_400_BAD_REQUEST)
