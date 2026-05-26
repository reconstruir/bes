#-*- coding:utf-8; mode:python; indent-tabs-mode: nil; c-basic-offset: 2; tab-width: 2 -*-

def bf_media_resolve_task(context, args):
  'btask worker: resolve one attr for a chunk of files.'
  entries   = args['entries']   # list of {'filename': str, 'mime_type': str}
  attr_name = args['attr_name']
  resolver  = args['resolver']  # bf_media_attr_resolver_base subclass

  results = []
  for entry_dict in entries:
    context.raise_cancelled_if_needed('resolve cancelled')
    try:
      value = resolver.resolve(entry_dict['filename'], entry_dict['mime_type'], attr_name)
      results.append({
        'filename': entry_dict['filename'],
        'attr_name': attr_name,
        'value': value,
      })
    except Exception:
      pass  # per-file errors silently omitted from results

  return {'results': results}
