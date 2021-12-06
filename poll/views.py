from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render,redirect
from django.views.generic import TemplateView, ListView

from poll.models import Candidate, Voter, Vote, Block
import math
from datetime import datetime
import time, datetime
from hashlib import sha512, sha256
from .merkleTree import merkleTree
import uuid
from django.conf import settings

resultCalculated = False


class HomeView(TemplateView):
    template_name = "poll/home.html"


class VoteView(ListView, LoginRequiredMixin):
    template_name = "poll/vote.html"

    def get_queryset(self):
        return Candidate.objects.filter(constituency=self.request.user.constituency)


def vote(request):
    candidates = Candidate.objects.all()
    context = {'candidates': candidates}
    return render(request, 'poll/vote.html', context)



def create(request, pk):
    voter = Voter.objects.filter(username=request.user.username)[0]
    if request.method == 'POST' and request.user.is_authenticated and not voter.has_voted:
        vote = pk
        lenVoteList = len(Vote.objects.all())
        if (lenVoteList > 0):
            block_id = math.floor(lenVoteList / 5) + 1
        else:
            block_id = 1

        priv_key = {'n': int(request.POST.get('privateKey_n')), 'd':int(request.POST.get('privateKey_d'))}
        pub_key = {'n':int(voter.public_key_n), 'e':int(voter.public_key_e)}
        # Create ballot as string vector
        timestamp = datetime.datetime.now().timestamp()
        ballot = "{}|{}".format(vote, timestamp)
        print('\ncasted ballot: {}\n'.format(ballot))
        h = int.from_bytes(sha512(ballot.encode()).digest(), byteorder='big')
        signature = pow(h, priv_key['d'], priv_key['n'])

        hfromSignature = pow(signature, pub_key['e'], pub_key['n'])

        if(hfromSignature == h):
            new_vote = Vote(vote=pk)
            new_vote.block_id = block_id
            new_vote.save()
            status = 'Ballot signed successfully'
            error = False
        else:
            status = 'Authentication Error'
            error = True
        context = {
            'ballot': ballot,
            'signature': signature,
            'status': status,
            'error': error,
        }
        print(error)
        if not error:
            return render(request, 'poll/status.html', context)

    return render(request, 'poll/failure.html', context)

prev_hash = '0' * 64

def seal(request):

    if request.method == 'POST':

        if (len(Vote.objects.all()) % 5 != 0):
            redirect("login")
        else:
            global prev_hash
            transactions = Vote.objects.order_by('block_id').reverse()
            transactions = list(transactions)[:5]
            block_id = transactions[0].block_id

            str_transactions = [str(x) for x in transactions]

            merkle_tree = merkleTree.merkleTree()
            merkle_tree.makeTreeFromArray(str_transactions)
            merkle_hash = merkle_tree.calculateMerkleRoot()

            nonce = 0
            timestamp = datetime.datetime.now().timestamp()

            while True:
                self_hash = sha256('{}{}{}{}'.format(prev_hash, merkle_hash, nonce, timestamp).encode()).hexdigest()
                if self_hash[0] == '0':
                    break
                nonce += 1
            
            block = Block(id=block_id,prev_hash=prev_hash,self_hash=self_hash,merkle_hash=merkle_hash,nonce=nonce,timestamp=timestamp)
            prev_hash = self_hash
            block.save()
            print('Block {} has been mined'.format(block_id))

    return redirect("home")

def retDate(v):
    v.timestamp = datetime.datetime.fromtimestamp(v.timestamp)
    return v

def verify(request):
    if request.method == 'GET':
        verification = ''
        tampered_block_list = verifyVotes()
        votes = []
        if tampered_block_list:
            verification = 'Verification Failed. Following blocks have been tampered --> {}.\
                The authority will resolve the issue'.format(tampered_block_list)
            error = True
        else:
            verification = 'Verification successful. All votes are intact!'
            error = False
            votes = Vote.objects.order_by('timestamp')
            votes = [retDate(x) for x in votes]
            
        context = {'verification':verification, 'error':error, 'votes':votes}
        return render(request, 'poll/verification.html', context)

def result(request):
    if request.method == "GET":
        global resultCalculated
        voteVerification = verifyVotes()
        if len(voteVerification):
                return render(request, 'poll/verification.html', {'verification':"Verification failed.\
                Votes have been tampered in following blocks --> {}. The authority \
                    will resolve the issue".format(voteVerification), 'error':True})

        if not resultCalculated:
            list_of_votes = Vote.objects.all()
            for vote in list_of_votes:
                candidate = Candidate.objects.filter(candidateID=vote.vote)[0]
                candidate.count += 1
                candidate.save()
                
            resultCalculated = True            

        context = {"candidates": Candidate.objects.order_by('count'), "winner": Candidate.objects.order_by('count').reverse()[0]}
        return render(request, 'poll/results.html', context)


def verifyVotes():
    block_count = Block.objects.count()
    tampered_block_list = []
    for i in range (1, block_count+1):
        block = Block.objects.get(id=i)
        transactions = Vote.objects.filter(block_id=i)
        str_transactions = [str(x) for x in transactions]

        merkle_tree = merkleTree.merkleTree()
        merkle_tree.makeTreeFromArray(str_transactions)
        merkle_tree.calculateMerkleRoot()

        if (block.merkle_hash == merkle_tree.getMerkleRoot()):
            continue
        else:
            tampered_block_list.append(i)

    return tampered_block_list