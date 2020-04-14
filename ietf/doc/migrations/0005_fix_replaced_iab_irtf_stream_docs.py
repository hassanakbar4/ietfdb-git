# Copyright The IETF Trust 2018-2020, All Rights Reserved
# -*- coding: utf-8 -*-
# Generated by Django 1.11.13 on 2018-05-03 12:16


from django.db import migrations

def forward(apps, schema_editor):
    Document = apps.get_model('doc','Document')
    State = apps.get_model('doc','State')

    iab_active = State.objects.get(type_id='draft-stream-iab',slug='active')
    iab_replaced = State.objects.get(type_id='draft-stream-iab',slug='repl')

    irtf_active = State.objects.get(type_id='draft-stream-irtf',slug='active')
    irtf_candidate = State.objects.get(type_id='draft-stream-irtf',slug='candidat')
    irtf_replaced = State.objects.get(type_id='draft-stream-irtf',slug='repl')
    irtf_dead = State.objects.get(type_id='draft-stream-irtf',slug='dead')

    doc = Document.objects.get(name='draft-flanagan-rfc-preservation')
    doc.states.remove(iab_active)
    doc.states.add(iab_replaced)

    doc = Document.objects.get(name='draft-trammell-semi-report')
    doc.states.remove(iab_active)
    doc.states.add(iab_replaced)
    
    doc = Document.objects.get(name='draft-nir-cfrg-chacha20-poly1305')
    doc.states.remove(irtf_candidate)
    doc.states.add(irtf_replaced)

    doc = Document.objects.get(name='draft-ladd-spake2')
    doc.states.remove(irtf_candidate)
    doc.states.add(irtf_replaced)

    doc = Document.objects.get(name='draft-lee-nfvrg-resource-management-service-chain')
    doc.states.remove(irtf_candidate)
    doc.states.add(irtf_replaced)

    doc = Document.objects.get(name='draft-keranen-t2trg-rest-iot')
    doc.states.remove(irtf_candidate)
    doc.states.add(irtf_replaced)
    
    doc = Document.objects.get(name='draft-josefsson-argon2')
    doc.states.remove(irtf_active)
    doc.states.add(irtf_replaced)

    doc = Document.objects.get(name='draft-tenoever-hrpc-research')
    doc.states.remove(irtf_active)
    doc.states.add(irtf_replaced)

    doc = Document.objects.get(name='draft-kutscher-icnrg-challenges')
    doc.states.remove(irtf_dead)
    doc.states.add(irtf_replaced)
        
def reverse(apps, schema_editor):
    Document = apps.get_model('doc','Document')
    State = apps.get_model('doc','State')

    iab_active = State.objects.get(type_id='draft-stream-iab',slug='active')
    iab_replaced = State.objects.get(type_id='draft-stream-iab',slug='repl')

    irtf_active = State.objects.get(type_id='draft-stream-irtf',slug='active')
    irtf_candidate = State.objects.get(type_id='draft-stream-irtf',slug='candidat')
    irtf_replaced = State.objects.get(type_id='draft-stream-irtf',slug='repl')
    irtf_dead = State.objects.get(type_id='draft-stream-irtf',slug='dead')

    doc = Document.objects.get(name='draft-flanagan-rfc-preservation')
    doc.states.add(iab_active)
    doc.states.remove(iab_replaced)

    doc = Document.objects.get(name='draft-trammell-semi-report')
    doc.states.add(iab_active)
    doc.states.remove(iab_replaced)
    
    doc = Document.objects.get(name='draft-nir-cfrg-chacha20-poly1305')
    doc.states.add(irtf_candidate)
    doc.states.remove(irtf_replaced)

    doc = Document.objects.get(name='draft-ladd-spake2')
    doc.states.add(irtf_candidate)
    doc.states.remove(irtf_replaced)

    doc = Document.objects.get(name='draft-lee-nfvrg-resource-management-service-chain')
    doc.states.add(irtf_candidate)
    doc.states.remove(irtf_replaced)

    doc = Document.objects.get(name='draft-keranen-t2trg-rest-iot')
    doc.states.add(irtf_candidate)
    doc.states.remove(irtf_replaced)
    
    doc = Document.objects.get(name='draft-josefsson-argon2')
    doc.states.add(irtf_active)
    doc.states.remove(irtf_replaced)

    doc = Document.objects.get(name='draft-tenoever-hrpc-research')
    doc.states.add(irtf_active)
    doc.states.remove(irtf_replaced)

    doc = Document.objects.get(name='draft-kutscher-icnrg-challenges')
    doc.states.add(irtf_dead)
    doc.states.remove(irtf_replaced)

class Migration(migrations.Migration):

    dependencies = [
        ('doc', '0004_add_draft_stream_replaced_states'),
    ]

    operations = [
        migrations.RunPython(forward, reverse)
    ]
