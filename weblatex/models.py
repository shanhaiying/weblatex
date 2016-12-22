from __future__ import division, absolute_import, unicode_literals

import re
import itertools

from django.db import models

from weblatex.fields import PositionField


def lyrics_as_tex(lyrics):
    lyrics = re.sub(r'\r+\n?', '\n', lyrics)
    lyrics = re.sub(r'^ +| +$', '', lyrics, 0, re.M)
    result = []
    paragraphs = re.split(r'\n\n+', lyrics)
    for p in paragraphs:
        if p.startswith('[Omk]'):
            p = p[5:].strip()
            kind = 'omkvaed'
        else:
            kind = 'vers'
        p = p.replace('´', '\'')
        lines = p.splitlines()
        result.append(
            '\\begin{%s}%%\n%s\end{%s}%%\n' %
            (kind, '\n\\verseend\n'.join(lines), kind))
    return ''.join('%s\n' % l for l in result)


def song_as_tex(name, attribution, lyrics, twocolumn=False):
    song_tex = lyrics_as_tex(lyrics)
    if twocolumn:
        song_tex = (
            r'\begin{multicols}{2}\multicolinit' +
            r'%s\end{multicols}' % song_tex
        )
    return (r'\begin{sang}{%s}{%s}%s\end{sang}' %
        (name, attribution, song_tex))


class Song(models.Model):
    name = models.CharField(max_length=100)
    attribution = models.CharField(max_length=200, blank=True)
    lyrics = models.TextField()

    def __str__(self):
        return self.name


class Booklet(models.Model):
    songs = models.ManyToManyField(Song, through='BookletEntry')

    def as_tex(self):
        songs = []
        for e in self.bookletentry_set.all():
            position = PositionField.parse_position(e.position)
            position = tuple((x1 or 1, x2 or 1) for x1, x2 in position)
            position_flat = tuple(x for xs in position for x in xs)
            songs.append((e.page, position_flat, e))
        songs.sort()
        pages = itertools.groupby(songs, key=lambda x: x[0])
        output = []
        for page, page_songs in pages:
            page_songs = [
                (position, entry) for page, position, entry in page_songs
            ]
            longest_position = max(
                len(position) for position, entry in page_songs)
            page_songs = [
                (position + (1,) * (longest_position - len(position)),
                 entry)
                for position, entry in page_songs
            ]
            render_stack = [(0, page_songs)]
            # output.append(r'\begin{multicols}{2}')
            while render_stack:
                disc, xs = render_stack.pop()
                if isinstance(disc, str):
                    output.append(disc)
                elif len(xs) == 1:
                    e = xs[0][1]
                    output.append(song_as_tex(
                        e.song.name,
                        e.song.attribution if e.attribution else '',
                        e.song.lyrics, e.twocolumn))
                else:
                    groups = itertools.groupby(xs, key=lambda x: x[0][disc])
                    children = [(disc + 1, list(group)) for _, group in groups]
                    if disc % 2 == 0:
                        # Vertical
                        for c in reversed(children):
                            render_stack.append(c)
                    else:
                        # Horizontal
                        for c in reversed(children):
                            render_stack.append((r'\end{minipage}%', None))
                            render_stack.append(c)
                            render_stack.append(
                                (r'\noindent\begin{minipage}[t]' +
                                 r'{%s\textwidth}%%' % (1/len(children)),
                                 None))
            # output.append(r'\end{multicols}')
            output.append(r'\clearpage')
        return '\n'.join(output)


class BookletEntry(models.Model):
    booklet = models.ForeignKey(Booklet)
    song = models.ForeignKey(Song)
    page = models.IntegerField()
    position = models.CharField(blank=True, max_length=50)

    twocolumn = models.BooleanField()
    attribution = models.BooleanField(default=True)

    class Meta:
        ordering = ['booklet', 'page', 'position']


class UploadedSong(models.Model):
    song = models.ForeignKey(Song)
    source = models.BinaryField()
    upload_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.song)
