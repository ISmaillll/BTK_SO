from .models import * 
from .serializers import * 
from django.views.decorators.csrf import csrf_exempt 
from rest_framework.generics import  ListCreateAPIView,RetrieveUpdateDestroyAPIView, RetrieveDestroyAPIView,ListAPIView
from django.http.response import JsonResponse 
from rest_framework.parsers import JSONParser 
from django.db.models import Q
from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from dateutil.relativedelta import relativedelta
from datetime import date
from scipy.stats import chi2
from rest_framework import status
from django.utils.dateparse import parse_date
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

class CreateMedecinView(generics.CreateAPIView):
    queryset = Medecin.objects.all()
    serializer_class = MedecinSerializer

class MedecinDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = MedecinSerializer(user)
        return Response(serializer.data)
    
class PatientListCreateView(ListCreateAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated]

class PatientRetrieveUpdateDeleteView(RetrieveUpdateDestroyAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer
    permission_classes = [IsAuthenticated]

class TraitementListCreateView(ListCreateAPIView):
    queryset = Traitement.objects.all()
    serializer_class = TraitementSerializer
    permission_classes = [IsAuthenticated]

class TraitementRetrieveUpdateDeleteView(RetrieveUpdateDestroyAPIView):
    queryset = Traitement.objects.all()
    serializer_class = TraitementSerializer
    permission_classes = [IsAuthenticated]

class ConsultationListCreateView(ListCreateAPIView):
    queryset = Consultation.objects.all()
    serializer_class = ConsultationSerializer
    permission_classes = [IsAuthenticated]

class ConsultationRetrieveUpdateDeleteView(RetrieveUpdateDestroyAPIView):
    queryset = Consultation.objects.all()
    serializer_class = ConsultationSerializer
    permission_classes = [IsAuthenticated]

class AntecedantsListCreateView(ListCreateAPIView):
    queryset = Antecedants.objects.all()
    serializer_class = AntecedantsSerializer
    permission_classes = [IsAuthenticated]

class AntecedantsRetrieveUpdateDeleteView(RetrieveUpdateDestroyAPIView):
    queryset = Antecedants.objects.all()
    serializer_class = AntecedantsSerializer
    permission_classes = [IsAuthenticated]

class traitementpatientCreateView(ListCreateAPIView):
    queryset = Traitement_Patient.objects.all()
    serializer_class = TraitementpatientSerializer
    permission_classes = [IsAuthenticated]

class traitementpatientRetrieveUpdateDeleteView(RetrieveUpdateDestroyAPIView):
    queryset = Traitement_Patient.objects.all()
    serializer_class = TraitementpatientSerializer
    permission_classes = [IsAuthenticated]

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def patients_by_traitement(request, traitement_id):
    traitement_patient_ids = Traitement_Patient.objects.filter(Id_T=traitement_id).values_list('Id_P', flat=True)
    patients = Patient.objects.filter(id__in=traitement_patient_ids)
    serializer = PatientSerializer(patients, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def TableSurvieView(request, TimeUnit , Step , Date_Debut=None, Date_Fin=None):

    try:
        if Date_Debut is None and Date_Fin is None:
            patients = Patient.objects.all()
        else:
            date_debut = parse_date(Date_Debut)
            date_fin = parse_date(Date_Fin)

            if date_debut is None or date_fin is None:
                return JsonResponse({'error': 'Invalid date format'}, status=400)
            
            patients = Patient.objects.filter(Date_Debut_P__lte=date_debut)
            
        Nbr_P1 = len(patients) 
        if Nbr_P1 > 0:
            table_p_data = CreatP(patients)
            Max_Time , Time_Field = setUnit(TimeUnit , table_p_data , Date_Debut , Date_Fin)

            _ , Temps_array ,F_S_array = Calsulat_F_S(Max_Time,Step,table_p_data,Time_Field)

            return JsonResponse({'Temps': Temps_array, 'F_S': F_S_array ,"Nbr_P1" : Nbr_P1 })
        else :
            return JsonResponse({'Temps': [], 'F_S': [] })
    except Exception as e:
        return JsonResponse({'Temps': [], 'F_S': [] ,'error':'An internal server error occurred'}, status=500)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def TraitementNonView(request, TimeUnit, Step, traitement_id, Date_Debut=None, Date_Fin=None):
    try:
        traitement_patient_ids = Traitement_Patient.objects.filter(Id_T=traitement_id).values_list('Id_P', flat=True)
        
        if Date_Debut is None and Date_Fin is None:
            patients1 = Patient.objects.filter(id__in=traitement_patient_ids)
            patients2 = Patient.objects.exclude(id__in=traitement_patient_ids)
        else:
            date_debut = parse_date(Date_Debut)
            date_fin = parse_date(Date_Fin)

            if date_debut is None or date_fin is None:
                return JsonResponse({'error': 'Invalid date format'}, status=400)

            patients1 = Patient.objects.filter(id__in=traitement_patient_ids, Date_Debut_P__lte=date_debut)
            patients2 = Patient.objects.exclude(id__in=traitement_patient_ids).filter(Date_Debut_P__lte=date_debut)

        traitement = Traitement.objects.get(id=traitement_id)
        traitement_type = traitement.Type

        Nbr_P1 = len(patients1) 
        Nbr_P2 = len(patients2) 

        if Nbr_P1 > 0 and Nbr_P2 > 0 :
            table_p_data1 = CreatP(patients1)
            table_p_data2 = CreatP(patients2)
            Max_Time, Time_Field = setUnit(TimeUnit, table_p_data1 , Date_Debut , Date_Fin)
            Max_Time2, _ = setUnit(TimeUnit, table_p_data2 , Date_Debut , Date_Fin)
            Max_Time = max(Max_Time, Max_Time2)

            survie_data1, Temps_array, F_S_array1 = Calsulat_F_S(Max_Time, Step, table_p_data1, Time_Field)
            survie_data2, _, F_S_array2 = Calsulat_F_S(Max_Time, Step, table_p_data2, Time_Field)

            p = Log_Rank(survie_data1, survie_data2)
            return JsonResponse({
                'Temps': Temps_array,
                'F_S1': F_S_array1,
                'F_S2': F_S_array2,
                'T1Type': traitement_type,
                'p': p,
                "Nbr_P1" : Nbr_P1,
                "Nbr_P2" : Nbr_P2
            })
        else :
            return JsonResponse({'Temps': [], 'F_S1': [], 'F_S2': [], 'error': 'No data'}, status=500)

    except Exception as e:
        return JsonResponse({'Temps': [], 'F_S1': [], 'F_S2': [], 'error': 'An internal server error occurred'}, status=500)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def Traitement12View(request, TimeUnit, Step, traitement_id1, traitement_id2, Date_Debut=None, Date_Fin=None):
    try:
        if Date_Debut is None and Date_Fin is None:
            traitement_patient_ids1 = Traitement_Patient.objects.filter(Id_T=traitement_id1).values_list('Id_P', flat=True)
            patients1 = Patient.objects.filter(id__in=traitement_patient_ids1)
            traitement_patient_ids2 = Traitement_Patient.objects.filter(Id_T=traitement_id2).values_list('Id_P', flat=True)
            patients2 = Patient.objects.filter(id__in=traitement_patient_ids2)
        else:
            date_debut = parse_date(Date_Debut)
            date_fin = parse_date(Date_Fin)

            if date_debut is None or date_fin is None:
                return JsonResponse({'error': 'Invalid date format'}, status=400)

            traitement_patient_ids1 = Traitement_Patient.objects.filter(Id_T=traitement_id1).values_list('Id_P', flat=True)
            patients1 = Patient.objects.filter(id__in=traitement_patient_ids1, Date_Debut_P__lte=date_debut)
            traitement_patient_ids2 = Traitement_Patient.objects.filter(Id_T=traitement_id2).values_list('Id_P', flat=True)
            patients2 = Patient.objects.filter(id__in=traitement_patient_ids2, Date_Debut_P__lte=date_debut)

        traitement1 = Traitement.objects.get(id=traitement_id1)
        traitement_type1 = traitement1.Type
        traitement2 = Traitement.objects.get(id=traitement_id2)
        traitement_type2 = traitement2.Type

        Nbr_P1 = len(patients1) 
        Nbr_P2 = len(patients2) 

        if Nbr_P1 > 0 and Nbr_P2 > 0 :
            table_p_data1 = CreatP(patients1)
            table_p_data2 = CreatP(patients2)
            Max_Time, Time_Field = setUnit(TimeUnit, table_p_data1 , Date_Debut , Date_Fin)
            Max_Time2, _ = setUnit(TimeUnit, table_p_data2 , Date_Debut , Date_Fin)
            Max_Time = max(Max_Time, Max_Time2)

            survie_data1, Temps_array, F_S_array1 = Calsulat_F_S(Max_Time, Step, table_p_data1, Time_Field)
            survie_data2, _, F_S_array2 = Calsulat_F_S(Max_Time, Step, table_p_data2, Time_Field)

            p = Log_Rank(survie_data1, survie_data2)

            return JsonResponse({
                'Temps': Temps_array,
                'F_S1': F_S_array1,
                'F_S2': F_S_array2,
                'T1Type': traitement_type1,
                'T2Type': traitement_type2,
                'p': p,
                "Nbr_P1" : Nbr_P1,
                "Nbr_P2" : Nbr_P2
            }, safe=False)
        else :
            return JsonResponse({'Temps': [], 'F_S1': [], 'F_S2': [], 'error': 'No data'}, status=500)
    except Exception as e:
        return JsonResponse({'Temps': [], 'F_S1': [], 'F_S2': [], 'error': 'An internal server error occurred'}, status=500)

def CreatP(patients):
    table_p_data = []
    for patient in patients:
        start_date = patient.Date_Debut_P
        end_date = patient.Date_Fin_P
        mois = (end_date.year - start_date.year) * 12 + end_date.month - start_date.month
        jours = (end_date - start_date).days
        Statut = 1 if patient.Statut else 0
        table_p_data.append({
            'id': patient.id,
            'mois': mois,
            'jours': jours,
            'Statut': Statut,
        })
    return table_p_data

def setUnit(TimeUnit,table_p_data,Date_Debut,Date_Fin):
    
    if Date_Debut is None and Date_Fin is None:
        if TimeUnit == 0 : Max_Time = max(p['jours'] for p in table_p_data)
        else : Max_Time = max(p['mois'] for p in table_p_data)
    else :
        date_debut = parse_date(Date_Debut)
        date_fin = parse_date(Date_Fin)
        if TimeUnit == 0: Max_Time = (date_fin - date_debut).days
        else : Max_Time = (date_fin.year - date_debut.year) * 12 + date_fin.month - date_debut.month
    if TimeUnit == 0 : Time_Field = 'jours'
    else : Time_Field = 'mois'
    return Max_Time , Time_Field

def  Calsulat_F_S(Max_Time,Step,table_p_data,Time_Field):

    Total_patients = len(table_p_data)
    survie_data = []
    Temps_array = []
    F_S_array = []
    
    for i in range(0, Max_Time + 1, Step):
        DCD = sum(1 for p in table_p_data if p['Statut'] == 1 and i > p[Time_Field])
        Vivant = Total_patients - DCD
        Exclus = 0
        Probab_Deces = DCD / (Vivant - Exclus) if Vivant - Exclus > 0 else 0
        Probab_survie = 1 - Probab_Deces
        F_S = Probab_survie * (F_S_array[-1] if F_S_array else 1)
        F_S = 0 if F_S < 0 else F_S
        Temps = i

        entry = {
            'Temps': Temps,
            'Vivant': Vivant,
            'DCD': DCD,
            'Exclus': Exclus,
            'Probab_Deces': Probab_Deces,
            'Probab_survie': Probab_survie,
            'F_S': F_S,
            'C':0
        }
        survie_data.append(entry)
        Temps_array.append(Temps)
        F_S_array.append(F_S)
    return survie_data , Temps_array , F_S_array

def Log_Rank(survie_data1, survie_data2):
    num_Zones = len(survie_data1)
    
    # Initialize C values for each survival data entry
    for i in range(num_Zones):
        X = (survie_data1[i]['DCD'] + survie_data2[i]['DCD']) / (survie_data1[i]['Vivant'] + survie_data2[i]['Vivant'])
        survie_data1[i]['C'] = survie_data1[i]['Vivant'] * X
        survie_data2[i]['C'] = survie_data2[i]['Vivant'] * X
    
    # Sum up the values for C and DCD in both datasets
    TC1 = sum(item['C'] for item in survie_data1)
    TC2 = sum(item['C'] for item in survie_data2)
    TD1 = sum(item['DCD'] for item in survie_data1)
    TD2 = sum(item['DCD'] for item in survie_data2)

    # Compute the chi-squared statistic
    khi_deux = ((TD1 - TC1) ** 2 / TC1) + ((TD2 - TC2) ** 2 / TC2)
    # Degrees of freedom (usually 1 for comparing two groups)
    df = 1
    
    # Calculate the p-value
    p_value = chi2.sf(khi_deux, df)

    return p_value

# multy condition
def Log_Rank_Multiple(survie_data_list):
    num_zones = len(survie_data_list[0])
    num_datasets = len(survie_data_list)
    
    # Initialize C values for each survival data entry
    for i in range(num_zones):
        total_DCD = sum(survie_data_list[j][i]['DCD'] for j in range(num_datasets))
        total_Vivant = sum(survie_data_list[j][i]['Vivant'] for j in range(num_datasets))
        X = total_DCD / total_Vivant
        for j in range(num_datasets):
            survie_data_list[j][i]['C'] = survie_data_list[j][i]['Vivant'] * X
    
    # Sum up the values for C and DCD in all datasets
    TC = [sum(survie_data_list[j][i]['C'] for i in range(num_zones)) for j in range(num_datasets)]
    TD = [sum(survie_data_list[j][i]['DCD'] for i in range(num_zones)) for j in range(num_datasets)]

    # Compute the chi-squared statistic
    khi_deux = sum(((TD[j] - TC[j]) ** 2 / TC[j]) for j in range(num_datasets))
    
    # Degrees of freedom (number of groups - 1)
    df = num_datasets - 1
    
    # Calculate the p-value
    p_value = chi2.sf(khi_deux, df)

    return p_value

def setUnitMulty(TimeUnit,table_p_data,len_patients,Date_Debut,Date_Fin):
    
    if Date_Debut == "" and Date_Fin == "":
        Max_Time = 0
        for i, P_data in enumerate(table_p_data) :
            if len_patients[i]>0:
                if TimeUnit == 0 : M = max(p['jours'] for p in P_data)
                else : M = max(p['mois'] for p in P_data)
        Max_Time = max(Max_Time, M)
    else :
        date_debut = parse_date(Date_Debut)
        date_fin = parse_date(Date_Fin)
        if TimeUnit == 0: Max_Time = (date_fin - date_debut).days
        else : Max_Time = (date_fin.year - date_debut.year) * 12 + date_fin.month - date_debut.month
    if TimeUnit == 0 : Time_Field = 'jours'
    else : Time_Field = 'mois'
    return Max_Time , Time_Field

def Dev_pateints(Date_Debut, Date_Fin, Cond, Inverse):
    patientsGroups = []
    Group_names = []
    
    if len(Cond) == 0:
        if Date_Debut =="" and Date_Fin =="":
            patientsGroups.append(list(Patient.objects.all()))
        else:
            date_debut = parse_date(Date_Debut)
            date_fin = parse_date(Date_Fin)

            if date_debut is None or date_fin is None:
                return [] , []
            
            patientsGroups.append(list(Patient.objects.filter(Date_Debut_P__lte=date_fin)))
        Group_names.append("ALL")
    else:
        for C in Cond:
            if C['Type'] == "tr":
                traitement_patient_ids1 = Traitement_Patient.objects.filter(Id_T=C['id']).values_list('Id_P', flat=True)
                patientsGroups.append(list(Patient.objects.filter(id__in=traitement_patient_ids1)))
                Group_names.append(C['Value'])
            else:
                filter_args = {C['Attribut']: C['Value']}
                patientsGroups.append(list(Patient.objects.filter(**filter_args)))
                Group_names.append(C['Attribut']+" "+C['Value'])
        
        if Inverse:
            for C in Cond:
                if C['Type'] == "tr":
                    traitement_patient_ids1 = Traitement_Patient.objects.filter(Id_T=C['id']).values_list('Id_P', flat=True)
                    patientsGroups.append(list(Patient.objects.exclude(id__in=traitement_patient_ids1)))
                    Group_names.append("Non " + C['Value'])
                else:
                    exclude_args = {C['Attribut']: C['Value']}
                    patientsGroups.append(list(Patient.objects.exclude(**exclude_args)))
                    Group_names.append("Non " +C['Attribut']+" "+C['Value'])
    return patientsGroups , Group_names

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def MulityCondSurvie(request):
    try:
        TimeUnit = request.data.get('TimeUnit')
        Step = request.data.get('Step')
        Date_Debut = request.data.get('Date_Debut', None)
        Date_Fin = request.data.get('Date_Fin', None)
        Cond = request.data.get('Cond')
        Inverse = request.data.get('Inverse')

        patientsGroups , Group_names = Dev_pateints(Date_Debut,Date_Fin,Cond,Inverse)
        print(Group_names)
        len_patients = []
        table_p_data = []
        survie_data = []
        Temps_array = []
        F_S_array = []
        for P in patientsGroups : 
            len_patients.append(len(P))
            table_p_data.append(CreatP(P))
                
        Max_Time , Time_Field = setUnitMulty(TimeUnit , table_p_data , len_patients , Date_Debut , Date_Fin)
        for i, P_data in enumerate(table_p_data) :
            survie_data_ , Temps_array ,F_S_array_ = Calsulat_F_S(Max_Time,Step,P_data,Time_Field)
            survie_data.append(survie_data_)
            F_S_array.append(F_S_array_)
        if  len(survie_data)>1:
            p = Log_Rank_Multiple(survie_data) 
        else : 
            p = -1
        return JsonResponse({
            'Temps': Temps_array,
            'F_S': F_S_array,
            'Group_names': Group_names,
            'p': p,
            "Nbr_P" : len_patients,
        }, safe=False)
    except Exception as e:
        return JsonResponse({
            'Temps': [],
            'F_S': [],
            'Group_names': [],
            'p': 0,
            "Nbr_P" : [],
        }, safe=False)
# #####
class TraitementsForPatient(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request, patient_id):
        traitements = Traitement_Patient.objects.filter(Id_P=patient_id)
        serializer = TraitementPatientidSerializer(traitements, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class AddTraitementPatient(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, patient_id, traitement_id):
        try:
            patient = Patient.objects.get(id=patient_id)
            traitement = Traitement.objects.get(id=traitement_id)
            Traitement_Patient.objects.create(Id_P=patient, Id_T=traitement)
            return Response(status=status.HTTP_201_CREATED)
        except Patient.DoesNotExist:
            return Response({"error": "Patient not found"}, status=status.HTTP_404_NOT_FOUND)
        except Traitement.DoesNotExist:
            return Response({"error": "Traitement not found"}, status=status.HTTP_404_NOT_FOUND)

class RemoveTraitementPatient(APIView):
    permission_classes = [IsAuthenticated]
    def delete(self, request, patient_id, traitement_id):
        try:
            traitments = Traitement_Patient.objects.filter(Id_P=patient_id, Id_T=traitement_id)
            if traitments.exists():
                traitments.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            else:
                return Response({"error": "Traitement_Patient not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)