from django.http import HttpResponse, HttpResponseRedirect, Http404

from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext

from django.core.mail import send_mail

from django import forms

from ebi.metagame.models import Player
from battleroyale.models import *

import actstream
from actstream.models import Action, actor_stream

import datetime, random, math, json

import logging

def klassement(request):
    styles = Style.objects.all()
    
    players = Player.objects.all().order_by('-rating')
    
    return render_to_response('metagame/klassement.html', {
        'players': players,
        'styles': styles,
        'current': 'klassement'
    }, context_instance=RequestContext(request))
    

def challenge(request):
    playerid = request.GET.get('target', None)

    target = get_object_or_404(Player, id=int(playerid))

    styles = Style.objects.all().order_by('name')

    return render_to_response('metagame/challenge_start.html', {
        'target': target,
        'styles': styles,
        'current': 'klassement'
    }, context_instance=RequestContext(request))


def challenge_detail(request, id):
    d = get_object_or_404(Duel, id=id)

    if d.open:
        styles = Style.objects.all().order_by('name')

        return render_to_response('metagame/challenge_open.html', {
            'duel': d,
            'styles': styles,
            'current': 'klassement'
        }, context_instance=RequestContext(request))
    else:
        return render_to_response('metagame/challenge_closed.html', {
            'duel': d,
            'current': 'klassement'
        }, context_instance=RequestContext(request))


def challenge_create(request):
    if request.method == 'POST':
        logging.debug('challenge post')
        # Trying to store a challenge

        challenger = request.user.get_profile()

        move_id = request.POST.get('move', None)
        logging.debug('got move id: %s', move_id)

        move = Move.objects.get(id=int(move_id))

        message = request.POST.get('message', '')
        logging.debug('got message: %s', message)

        target_id = request.POST.get('target', None)
        target = Player.objects.get(id=int(target_id))

        # Create Round object
        d = Duel(challenger=challenger, challenge_move=move, challenge_message=message, target=target)
        
        d.challenger_oldrank = challenger.get_rank()
        d.responder_oldrank = target.get_rank()

        awesomeness = d.get_challenge_awesomeness()
        d.challenge_awesomeness = awesomeness
        d.save()

        actstream.action.send(request.user, verb='heeft net %s uitgedaagd voor een duel' % target.user.username, target=d)

        d.send_target_message()
        
        return HttpResponse(json.dumps({
            'awesomeness': awesomeness
        }), mimetype='text/json')

def challenge_resolve(request):
    if request.method == 'POST':
        duel_id = int(request.POST.get('duel', None))
        d = Duel.objects.get(id=duel_id)
    
        d.open = False
        d.responded = datetime.datetime.now()
    
        move_id = int(request.POST.get('move', None))
        d.response_move = Move.objects.get(id=move_id)
    
        d.response_message = request.POST.get('message', '')
        d.response_awesomeness = d.get_response_awesomeness()
        d.save()
        
        result = {
            'awesomeness': d.response_awesomeness
        }
        
        if d.is_tie():
            players = [d.challenger, d.target]
            
            d.challenger.rating += 1
            d.target.rating += 1
            
            d.challenger_rating = d.challenger.rating
            d.repsonder_rating = d.target.rating
            
            phrase = 'Helaas, gelijkspel. Probeer het nog eens!'            
            result['phrase'] = phrase
            
            d.challenger.save()
            d.target.save()
            
            try:
                sw = Skill.objects.get(player=d.challenger, style=d.challenge_move.style)
                sw.progress('T')
                d.challenger_skilllevel = sw.level
                
                sl = Skill.objects.get(player=d.target, style=d.response_move.style)
                sl.progress('T')
                d.responder_skilllevel = sl.level
            except Skill.DoesNotExist:
                logging.error('Skills do not exist')
        else:
            winner = d.get_winner()
            winner_style = d.get_winner_style()
            loser = d.get_loser()
            loser_style = d.get_loser_style()
            
            result['winner'] = winner.user.username
            result['loser'] = loser.user.username
            
            try:
                winPhrase = WinPhrase.objects.get(style=winner_style)
                result['phrase'] = winPhrase.phrase
            except: 
                result['phrase'] = 'Generic win phrase.'
            
            try:
                sw = Skill.objects.get(player=winner, style=winner_style)
                sw.progress('W')
                
                sl = Skill.objects.get(player=loser, style=loser_style)
                sl.progress('L')
                
                # Fill in the current levels of both players
            except Skill.DoesNotExist:
                logging.error('Skills do not exist')
                
            # Update rating for both players
            # TODO for now naive rating update
            winner.rating += 3
            loser.rating -= 1
            winner.save()
            loser.save()
            
            if d.challenger == winner:
                d.challenger_skilllevel = sw.level
                d.responder_skilllevel = sl.level
                
                d.challenger_rating = winner.rating
                d.responder_rating = loser.rating
            else:
                d.challenger_skilllevel = sl.level
                d.responder_skilllevel = sw.level
                
                d.challenger_rating = loser.rating
                d.responder_rating = winner.rating
            
            d.challenger_newrank = d.challenger.get_rank()
            d.responder_newrank = d.target.get_rank()
        
        d.save()
        
        d.send_winner_loser_messages()
        
        return HttpResponse(json.dumps(result), mimetype="text/json")
        
def challenge_detail_redirect(request, id):
    return HttpResponseRedirect('/challenge/%s/' % id)