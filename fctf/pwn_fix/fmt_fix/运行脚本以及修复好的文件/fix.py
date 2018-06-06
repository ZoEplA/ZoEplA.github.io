#!/usr/bin/env python
# coding=utf-8


def format_string(pt):
    buf = pt.inject(raw = "%s\x00")
    format_string = 0x40085E
    addr = pt.inject(asm='mov rsi, rdi; lea rdi, [rip-0xD]; ret')
    pt.hook(format_string, addr)
