#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

def bf_media_resolve_task(context, args):
  'btask worker: resolve one feature for a chunk of files.'
  entries      = args['entries']       # list of {'filename': str, 'mime_type': str}
  feature_name = args['feature_name']
  resolver     = args['resolver']      # bf_media_feature_resolver_base subclass

  results = []
  for entry_dict in entries:
    context.raise_cancelled_if_needed('resolve cancelled')
    try:
      value = resolver.resolve(entry_dict['filename'], entry_dict['mime_type'], feature_name)
      results.append({
        'filename':     entry_dict['filename'],
        'feature_name': feature_name,
        'value':        value,
      })
    except Exception:
      pass  # per-file errors silently omitted from results

  return {'results': results}
