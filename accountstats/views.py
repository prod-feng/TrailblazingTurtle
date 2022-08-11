from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from userportal.common import account_or_staff, Prometheus
from userportal.common import compute_allocations_by_user, compute_allocations_by_slurm_account

from django.core.paginator import Paginator
from slurm.models import JobTable, AssocTable

LONG_PERIOD = timedelta(days=60)
SHORT_PERIOD = timedelta(days=14)

prom = Prometheus(settings.PROMETHEUS)


@login_required
def index(request):
    context = {}
    username = request.META['username']
    context['compute_allocations'] = compute_allocations_by_user(username)
    return render(request, 'accountstats/index.html', context)


@login_required
@account_or_staff
def account(request, account):
    context = {}
    allocation = compute_allocations_by_slurm_account(account)
    if allocation is not None:
        if 'gpu' in allocation:
            context['gpu'] = True
            context['gpu_count'] = allocation['gpu']
        if 'cpu' in allocation:
            context['gpu'] = False
            context['cpu_count'] = allocation['cpu']

    # jobtable is not indexed by account, so we need to get assocs for this account, that one is indexed
    assocs = []
    for assoc in AssocTable.objects.filter(acct=account):
        assocs.append(assoc.id_assoc)

    jobs = JobTable.objects.filter(id_assoc__in=assocs).order_by('-time_submit')
    paginator = Paginator(jobs, 100)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context['jobs'] = page_obj

    return render(request, 'accountstats/account.html', context)


@login_required
@account_or_staff
def graph_cpu_allocated(request, account):
    data = {'lines': []}
    query_alloc = 'sum(slurm_job:allocated_core:count_user_account{{account="{}", {}}}) by (user)'.format(account, prom.get_filter())
    stats_alloc = prom.query_prometheus_multiple(query_alloc, datetime.now() - SHORT_PERIOD, datetime.now())

    for line in stats_alloc:
        user = line['metric']['user']
        x = list(map(lambda x: x.strftime('%Y-%m-%d %H:%M:%S'), line['x']))
        y = line['y']
        data['lines'].append({
            'x': x,
            'y': y,
            'type': 'scatter',
            'stackgroup': 'one',
            'name': user
        })
    data['layout'] = {'showlegend': True}

    return JsonResponse(data)


@login_required
@account_or_staff
def graph_cpu_used(request, account):
    data = {'lines': []}
    query_used = 'sum(slurm_job:used_core:sum_user_account{{account="{}", {}}}) by (user)'.format(account, prom.get_filter())
    stats_used = prom.query_prometheus_multiple(query_used, datetime.now() - SHORT_PERIOD, datetime.now())

    for line in stats_used:
        user = line['metric']['user']
        x = list(map(lambda x: x.strftime('%Y-%m-%d %H:%M:%S'), line['x']))
        y = line['y']
        data['lines'].append({
            'x': x,
            'y': y,
            'type': 'scatter',
            'stackgroup': 'one',
            'name': user
        })
    data['layout'] = {'showlegend': True}

    return JsonResponse(data)


@login_required
@account_or_staff
def graph_cpu_wasted(request, account):
    data = {'lines': []}
    query_alloc = 'clamp_min(sum(slurm_job:allocated_core:count_user_account{{account="{}", {}}}) by (user) - sum(slurm_job:used_core:sum_user_account{{account="{}", {}}}) by (user), 0)'.format(account, prom.get_filter(), account, prom.get_filter())
    stats_alloc = prom.query_prometheus_multiple(query_alloc, datetime.now() - SHORT_PERIOD, datetime.now())

    for line in stats_alloc:
        user = line['metric']['user']
        x = list(map(lambda x: x.strftime('%Y-%m-%d %H:%M:%S'), line['x']))
        y = line['y']
        data['lines'].append({
            'x': x,
            'y': y,
            'type': 'scatter',
            'name': user
        })
    data['layout'] = {'showlegend': True}

    return JsonResponse(data)


@login_required
@account_or_staff
def graph_mem_allocated(request, account):
    data = {'lines': []}
    query_alloc = 'sum(slurm_job:allocated_memory:sum_user_account{{account="{}", {}}}) by (user) /(1024*1024*1024)'.format(account, prom.get_filter())
    stats_alloc = prom.query_prometheus_multiple(query_alloc, datetime.now() - SHORT_PERIOD, datetime.now())

    for line in stats_alloc:
        user = line['metric']['user']
        x = list(map(lambda x: x.strftime('%Y-%m-%d %H:%M:%S'), line['x']))
        y = line['y']
        data['lines'].append({
            'x': x,
            'y': y,
            'type': 'scatter',
            'stackgroup': 'one',
            'name': user
        })

    data['layout'] = {
        'yaxis': {
            'ticksuffix': 'GiB',
        },
        'showlegend': True
    }

    return JsonResponse(data)


@login_required
@account_or_staff
def graph_mem_used(request, account):
    data = {'lines': []}
    query_used = 'sum(slurm_job:rss_memory:sum_user_account{{account="{}", {}}}) by (user) /(1024*1024*1024)'.format(account, prom.get_filter())
    stats_used = prom.query_prometheus_multiple(query_used, datetime.now() - SHORT_PERIOD, datetime.now())

    for line in stats_used:
        user = line['metric']['user']
        x = list(map(lambda x: x.strftime('%Y-%m-%d %H:%M:%S'), line['x']))
        y = line['y']
        data['lines'].append({
            'x': x,
            'y': y,
            'type': 'scatter',
            'stackgroup': 'one',
            'name': user,
        })

    data['layout'] = {
        'yaxis': {
            'ticksuffix': 'GiB',
        },
        'showlegend': True
    }

    return JsonResponse(data)


@login_required
@account_or_staff
def graph_mem_wasted(request, account):
    data = {'lines': []}
    query_alloc = 'clamp_min(sum(slurm_job:allocated_memory:sum_user_account{{account="{}", {}}}) by (user) - sum(slurm_job:rss_memory:sum_user_account{{account="{}", {}}}) by (user), 0) /(1024*1024*1024)'.format(account, prom.get_filter(), account, prom.get_filter())
    stats_alloc = prom.query_prometheus_multiple(query_alloc, datetime.now() - SHORT_PERIOD, datetime.now())

    for line in stats_alloc:
        user = line['metric']['user']
        x = list(map(lambda x: x.strftime('%Y-%m-%d %H:%M:%S'), line['x']))
        y = line['y']
        data['lines'].append({
            'x': x,
            'y': y,
            'type': 'scatter',
            'name': user
        })

    data['layout'] = {
        'yaxis': {
            'ticksuffix': 'GiB',
        },
        'showlegend': True
    }

    return JsonResponse(data)


@login_required
@account_or_staff
def graph_lustre_mdt(request, account):
    query = 'sum(rate(lustre_job_stats_total{{component=~"mdt",account=~"{}", {}}}[5m])) by (user, fs) !=0'.format(account, prom.get_filter())
    stats = prom.query_prometheus_multiple(query, datetime.now() - timedelta(hours=6), datetime.now())
    data = {'lines': []}
    for line in stats:
        user = line['metric']['user']
        fs = line['metric']['fs']
        x = list(map(lambda x: x.strftime('%Y-%m-%d %H:%M:%S'), line['x']))
        y = line['y']
        data['lines'].append({
            'x': x,
            'y': y,
            'type': 'scatter',
            'stackgroup': 'one',
            'name': '{} {}'.format(user, fs)
        })

    data['layout'] = {
        'yaxis': {
            'ticksuffix': ' IOPS'
        },
        'showlegend': True
    }
    return JsonResponse(data)


@login_required
@account_or_staff
def graph_lustre_ost(request, account):
    data = {'lines': []}
    for i in ['read', 'write']:
        query = '(sum(rate(lustre_job_{}_bytes_total{{component=~"ost",account=~"{}",target=~".*-OST.*", {}}}[5m])) by (user, fs)) / (1024*1024)'.format(i, account, prom.get_filter())
        stats = prom.query_prometheus_multiple(query, datetime.now() - timedelta(hours=6), datetime.now())

        for line in stats:
            fs = line['metric']['fs']
            user = line['metric']['user']
            x = list(map(lambda x: x.strftime('%Y-%m-%d %H:%M:%S'), line['x']))
            if i == 'read':
                y = line['y']
            else:
                y = [-x for x in line['y']]
            data['lines'].append({
                'x': x,
                'y': y,
                'type': 'scatter',
                'name': '{} {} {}'.format(i, fs, user)
            })

    data['layout'] = {
        'yaxis': {
            'ticksuffix': ' MiB/s'
        },
        'showlegend': True
    }
    return JsonResponse(data)


@login_required
@account_or_staff
def graph_gpu_allocated(request, account):
    query = 'sum(slurm_job:allocated_gpu:count_user_account{{account="{}", {}}}) by (user)'.format(account, prom.get_filter())
    stats = prom.query_prometheus_multiple(query, datetime.now() - SHORT_PERIOD, datetime.now())

    data = {'lines': []}
    for line in stats:
        x = list(map(lambda x: x.strftime('%Y-%m-%d %H:%M:%S'), line['x']))
        y = line['y']
        data['lines'].append({
            'x': x,
            'y': y,
            'type': 'scatter',
            'stackgroup': 'one',
            'name': line['metric']['user']
        })
    data['layout'] = {'showlegend': True}

    return JsonResponse(data)


@login_required
@account_or_staff
def graph_gpu_used(request, account):
    query = 'sum(slurm_job:used_gpu:sum_user_account{{account="{}", {}}}) by (user)'.format(account, prom.get_filter())
    stats = prom.query_prometheus_multiple(query, datetime.now() - SHORT_PERIOD, datetime.now())

    data = {'lines': []}
    for line in stats:
        x = list(map(lambda x: x.strftime('%Y-%m-%d %H:%M:%S'), line['x']))
        y = line['y']
        data['lines'].append({
            'x': x,
            'y': y,
            'type': 'scatter',
            'stackgroup': 'one',
            'name': line['metric']['user']
        })
    data['layout'] = {'showlegend': True}

    return JsonResponse(data)


@login_required
@account_or_staff
def graph_gpu_wasted(request, account):
    query = 'sum(slurm_job:allocated_gpu:count_user_account{{account="{}", {}}}) by (user) - sum(slurm_job:used_gpu:sum_user_account{{account="{}", {}}}) by (user)'.format(account, prom.get_filter(), account, prom.get_filter())
    stats = prom.query_prometheus_multiple(query, datetime.now() - SHORT_PERIOD, datetime.now())

    data = {'lines': []}
    for line in stats:
        x = list(map(lambda x: x.strftime('%Y-%m-%d %H:%M:%S'), line['x']))
        y = line['y']
        data['lines'].append({
            'x': x,
            'y': y,
            'type': 'scatter',
            'name': line['metric']['user']
        })
    data['layout'] = {'showlegend': True}

    return JsonResponse(data)


@login_required
@account_or_staff
# kinda broken when using multiple GPUs
def graph_gpu_power_allocated(request, account):
    query = 'count(slurm_job_power_gpu{{account="{}", {}}}) by (user) * 300'.format(account, prom.get_filter())
    stats = prom.query_prometheus_multiple(query, datetime.now() - timedelta(hours=6), datetime.now())

    data = {'lines': []}
    for line in stats:
        x = list(map(lambda x: x.strftime('%Y-%m-%d %H:%M:%S'), line['x']))
        y = line['y']
        data['lines'].append({
            'x': x,
            'y': y,
            'type': 'scatter',
            'stackgroup': 'one',
            'name': line['metric']['user']
        })
    data['layout'] = {
        'yaxis': {
            'ticksuffix': ' W',
        },
        'showlegend': True
    }

    return JsonResponse(data)


@login_required
@account_or_staff
# kinda broken when using multiple GPUs
def graph_gpu_power_used(request, account):
    query = 'sum(slurm_job_power_gpu{{account="{}", {}}}) by (user) / 1000'.format(account, prom.get_filter())
    stats = prom.query_prometheus_multiple(query, datetime.now() - timedelta(hours=6), datetime.now())

    data = {'lines': []}
    for line in stats:
        x = list(map(lambda x: x.strftime('%Y-%m-%d %H:%M:%S'), line['x']))
        y = line['y']
        data['lines'].append({
            'x': x,
            'y': y,
            'type': 'scatter',
            'stackgroup': 'one',
            'name': line['metric']['user']
        })
    data['layout'] = {
        'yaxis': {
            'ticksuffix': ' W',
        },
        'showlegend': True
    }

    return JsonResponse(data)


@login_required
@account_or_staff
# kinda broken when using multiple GPUs
def graph_gpu_power_wasted(request, account):
    query = '(count(slurm_job_power_gpu{{account="{}", {}}}) by (user) * 300) - (sum(slurm_job_power_gpu{{account="{}", {}}}) by (user) / 1000)'.format(account, prom.get_filter(), account, prom.get_filter())
    stats = prom.query_prometheus_multiple(query, datetime.now() - timedelta(hours=6), datetime.now())

    data = {'lines': []}
    for line in stats:
        x = list(map(lambda x: x.strftime('%Y-%m-%d %H:%M:%S'), line['x']))
        y = line['y']
        data['lines'].append({
            'x': x,
            'y': y,
            'type': 'scatter',
            'stackgroup': 'one',
            'name': line['metric']['user']
        })
    data['layout'] = {
        'yaxis': {
            'ticksuffix': ' W',
        },
        'showlegend': True
    }

    return JsonResponse(data)


@login_required
@account_or_staff
def graph_cpu_priority(request, account):
    return graph_cpu_or_gpu_priority(request, account, 'cpu')


@login_required
@account_or_staff
def graph_gpu_priority(request, account):
    return graph_cpu_or_gpu_priority(request, account, 'gpu')


# auth done in functions above
def graph_cpu_or_gpu_priority(request, account, gpu_or_cpu):
    data = {'lines': []}
    if gpu_or_cpu == 'gpu':
        query_alloc = 'sum(slurm_job:allocated_gpu:count_user_account{{account="{}", {}}}) or vector(0)'.format(account, prom.get_filter())
    else:
        query_alloc = 'sum(slurm_job:allocated_core:count_user_account{{account="{}", {}}}) or vector(0)'.format(account, prom.get_filter())
    stats_alloc = prom.query_prometheus(query_alloc, datetime.now() - LONG_PERIOD, datetime.now(), step='1h')

    x = list(map(lambda x: x.strftime('%Y-%m-%d %H:%M:%S'), stats_alloc[0]))
    y = stats_alloc[1]
    allocated = {
        'x': x,
        'y': y,
        'type': 'scatter',
        'name': 'Allocated cores',
        'yaxis': 'y1',
    }
    if gpu_or_cpu == 'gpu':
        allocated['name'] = 'Allocated GPUs'
    else:
        allocated['name'] = 'Allocated cores'
    data['lines'].append(allocated)

    allocation = compute_allocations_by_slurm_account(account)
    if allocation is not None:
        if 'gpu' in allocation:
            alloc = allocation['gpu']
        if 'cpu' in allocation:
            alloc = allocation['cpu']
    else:
        alloc = 0
    if(account.startswith('def-') is False):
        data['lines'].append({
            'x': x,
            'y': [alloc] * len(x),
            'type': 'scatter',
            'name': 'Allocation',
            'yaxis': 'y1',
        })

    if gpu_or_cpu == 'gpu':
        query_used = 'sum(slurm_job:used_gpu:sum_user_account{{account="{}", {}}}) or vector(0)'.format(account, prom.get_filter())
    else:
        query_used = 'sum(slurm_job:used_core:sum_user_account{{account="{}", {}}}) or vector(0)'.format(account, prom.get_filter())
    stats_used = prom.query_prometheus(query_used, datetime.now() - LONG_PERIOD, datetime.now(), step='1h')

    x = list(map(lambda x: x.strftime('%Y-%m-%d %H:%M:%S'), stats_used[0]))
    y = stats_used[1]
    used = {
        'x': x,
        'y': y,
        'type': 'scatter',
        'yaxis': 'y1',
    }
    if gpu_or_cpu == 'gpu':
        used['name'] = 'Used GPUs'
    else:
        used['name'] = 'Used cores'
    data['lines'].append(used)

    query_levelfs = 'slurm_account_levelfs{{account="{}", {}}}'.format(account, prom.get_filter())
    stats_levelfs = prom.query_prometheus(query_levelfs, datetime.now() - LONG_PERIOD, datetime.now(), step='1h')

    x = list(map(lambda x: x.strftime('%Y-%m-%d %H:%M:%S'), stats_levelfs[0]))
    y = stats_levelfs[1]
    data['lines'].append({
        'x': x,
        'y': y,
        'type': 'scatter',
        'name': 'Priority',
        'yaxis': 'y2',
    })

    if gpu_or_cpu == 'gpu':
        title = 'GPUs'
    else:
        title = 'Cores'
    data['layout'] = {
        'yaxis': {
            'title': title,
            'range': [0, max(stats_alloc[1])],
        },
        'yaxis2': {
            'title': 'Priority',
            'overlaying': 'y',
            'side': 'right',
            'range': [0, max(stats_levelfs[1])],
        },
        'showlegend': True,
    }

    return JsonResponse(data)
