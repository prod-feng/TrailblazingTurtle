from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),
    path('<str:username>/', views.user),
    path('<str:username>/graph/cpu.json', views.graph_cpu_user),
    path('<str:username>/graph/mem.json', views.graph_mem_user),
    path('<str:username>/graph/lustre_mdt.json', views.graph_lustre_mdt_user),
    path('<str:username>/graph/lustre_ost.json', views.graph_lustre_ost_user),
    path('<str:username>/graph/gpu_utilization.json', views.graph_gpu_utilization_user),
    path('<str:username>/graph/gpu_power.json', views.graph_gpu_power_user),
    path('<str:username>/<str:job_id>/', views.job),
    path('<str:username>/<str:job_id>/graph/cpu.json', views.graph_cpu),
    path('<str:username>/<str:job_id>/graph/mem.json', views.graph_mem),
    path('<str:username>/<str:job_id>/graph/lustre_mdt.json', views.graph_lustre_mdt),
    path('<str:username>/<str:job_id>/graph/lustre_ost.json', views.graph_lustre_ost),
    path('<str:username>/<str:job_id>/graph/gpu_utilization.json', views.graph_gpu_utilization),
    path('<str:username>/<str:job_id>/graph/gpu_memory_utilization.json', views.graph_gpu_memory_utilization),
    path('<str:username>/<str:job_id>/graph/gpu_memory.json', views.graph_gpu_memory),
    path('<str:username>/<str:job_id>/graph/gpu_power.json', views.graph_gpu_power),
    path('<str:username>/<str:job_id>/graph/gpu_pcie.json', views.graph_gpu_pcie),
    path('<str:username>/<str:job_id>/graph/gpu_nvlink.json', views.graph_gpu_nvlink),
    path('<str:username>/<str:job_id>/graph/infiniband_bdw.json', views.graph_infiniband_bdw),
    path('<str:username>/<str:job_id>/graph/disk_iops.json', views.graph_disk_iops),
    path('<str:username>/<str:job_id>/graph/disk_bdw.json', views.graph_disk_bdw),
    path('<str:username>/<str:job_id>/graph/disk_used.json', views.graph_disk_used),
    path('<str:username>/<str:job_id>/graph/power.json', views.graph_power),
    path('<str:username>/<str:job_id>/value/cost.json', views.value_cost),
]
