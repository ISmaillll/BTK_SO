from django.urls import path
from .views  import * 

from django.conf.urls.static import static
from django.conf import settings
from rest_framework_simplejwt.views import (TokenObtainPairView,TokenRefreshView,TokenVerifyView,)

urlpatterns=[
    path('register/', CreateMedecinView.as_view(), name='register'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('me/', MedecinDetailView.as_view(), name='user_detail'),
    #Patient
    path('Patient/', PatientListCreateView.as_view(), name='Patient-list-create'),
    path('Patient/<int:pk>/', PatientRetrieveUpdateDeleteView.as_view(), name='Patient-retrieve-update-delete'),
      #Traitement
    path('Traitement/', TraitementListCreateView.as_view(), name='Traitement-list-create'),
    path('Traitement/<int:pk>/', TraitementRetrieveUpdateDeleteView.as_view(), name='Traitement-retrieve-update-delete'),
      #Consultation
    path('Consultation/', ConsultationListCreateView.as_view(), name='Consultation-list-create'),
    path('Consultation/<int:pk>/', ConsultationRetrieveUpdateDeleteView.as_view(), name='Consultation-retrieve-update-delete'),
      #Antecedants
    path('Antecedants/', AntecedantsListCreateView.as_view(), name='Antecedants-list-create'),
    path('Antecedants/<int:pk>/', AntecedantsRetrieveUpdateDeleteView.as_view(), name='Antecedants-retrieve-update-delete'),
    # traitement_patient
    path('traitement-patient/', traitementpatientCreateView.as_view(), name='traitementpatient-list-create'),
    path('traitement-patient/<int:pk>/', traitementpatientRetrieveUpdateDeleteView.as_view(), name='traitementpatient-retrieve-update-destroy'),
    path('patients-by-traitement/<int:traitement_id>/', patients_by_traitement, name='patients-by-traitement'),
    # table-survie
    path('table-survie/<int:TimeUnit>/<int:Step>/', TableSurvieView, name='table_survie') ,
    path('CompaireTNonT/<int:TimeUnit>/<int:Step>/<int:traitement_id>/', TraitementNonView, name='table_survie') ,
    path('CompaireT1T2/<int:TimeUnit>/<int:Step>/<int:traitement_id1>/<int:traitement_id2>/', Traitement12View, name='table_survie') ,

    path('table-survie/', MulityCondSurvie, name='table_survie') ,
    path('table-survie/<int:TimeUnit>/<int:Step>/<str:Date_Debut>/<str:Date_Fin>/', TableSurvieView, name='table_survie') ,
    path('CompaireTNonT/<int:TimeUnit>/<int:Step>/<int:traitement_id>/<str:Date_Debut>/<str:Date_Fin>/', TraitementNonView, name='table_survie') ,
    path('CompaireT1T2/<int:TimeUnit>/<int:Step>/<int:traitement_id1>/<int:traitement_id2>/<str:Date_Debut>/<str:Date_Fin>/', Traitement12View, name='table_survie') ,
    path('idtraitement/<int:patient_id>/', TraitementsForPatient.as_view(), name='patient-traitements'),

    path('patient/<int:patient_id>/add_traitement/<int:traitement_id>/', AddTraitementPatient.as_view(), name='add-traitement-patient'),
    path('patient/<int:patient_id>/remove_traitement/<int:traitement_id>/', RemoveTraitementPatient.as_view(), name='remove-traitement-patient'),


]+static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)