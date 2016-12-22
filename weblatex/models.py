from __future__ import division, absolute_import, unicode_literals

import io
import re
import itertools

from django.db import models

from weblatex.fields import PositionField
from weblatex import layout


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
    front_text = models.TextField(blank=True)
    front_image = models.FileField(blank=True)
    contents = models.BooleanField(default=True)

    def layout_song(self, entries):
        (pos, entry), = entries
        return layout.Song(
            entry.song.name,
            entry.song.attribution if entry.attribution else '',
            entry.song.lyrics, entry.twocolumn)

    def layout_rows(self, entries, index):
        def key(x):
            return x[0][index][0]

        t = layout.Rows

        def rec(x):
            return self.layout_cols(x, index)

        if len(entries) == 1:
            return self.layout_song(entries)
        if len(set(map(key, entries))) == 1:
            return rec(entries)
        return t([rec(list(g))
                  for _, g in itertools.groupby(entries, key=key)])

    def layout_cols(self, entries, index):
        def key(x):
            return x[0][index][1]

        t = layout.Cols

        def rec(x):
            return self.layout_rows(x, index+1)

        if len(entries) == 1:
            return self.layout_song(entries)
        if len(set(map(key, entries))) == 1:
            return rec(entries)
        return t([rec(list(g))
                  for _, g in itertools.groupby(entries, key=key)])

    def as_tex(self):
        layout_pages = []
        all_entries = self.bookletentry_set.all()
        all_entries = all_entries.order_by('page', 'position', 'song')
        pages = itertools.groupby(all_entries, key=lambda e: e.page)
        for page, entries in pages:
            entries = ((PositionField.parse_position(e.position), e)
                       for e in entries)
            layout_pages.append(layout.Page(
                self.layout_rows(list(entries), 0)))
        buf = io.StringIO()
        for p in layout_pages:
            p.render(buf)
        return buf.getvalue()


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
