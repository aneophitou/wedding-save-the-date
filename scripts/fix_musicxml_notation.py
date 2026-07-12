#!/usr/bin/env python3
"""Rewrite corrupted MusicXML notation while preserving sounding durations."""

from __future__ import annotations

import argparse
import copy
import math
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from fractions import Fraction
from pathlib import Path
from typing import Iterable

DIVISIONS = 48
CANDIDATE_METERS: tuple[tuple[int, int], ...] = (
    (2, 4),
    (3, 4),
    (4, 4),
    (5, 4),
    (6, 4),
    (6, 8),
    (9, 8),
    (12, 8),
)

NOTE_TYPES: tuple[tuple[str, int], ...] = (
    ("whole", 192),
    ("half", 96),
    ("quarter", 48),
    ("eighth", 24),
    ("16th", 12),
    ("32nd", 6),
)


@dataclass
class SoundEvent:
    offset: Fraction
    duration: Fraction
    pitches: tuple[tuple[str, int | None, int], ...] = ()
    is_rest: bool = False
    tie_start: bool = False
    tie_stop: bool = False
    technical: list[ET.Element] = field(default_factory=list)
    accidentals: dict[tuple[str, int | None, int], str] = field(default_factory=dict)
    articulations: list[ET.Element] = field(default_factory=list)
    stem: str | None = None

    @property
    def end(self) -> Fraction:
        return self.offset + self.duration


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "input",
        type=Path,
        nargs="?",
        default=Path("/home/ubuntu/.cursor/projects/workspace/uploads/Duplicate-of-obsidian_d468.xml"),
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=Path("/home/ubuntu/.cursor/projects/workspace/uploads/Duplicate-of-obsidian_d468-fixed.xml"),
    )
    parser.add_argument("--parts", default="P1,P2")
    parser.add_argument("--from-measure", type=int, default=1)
    parser.add_argument("--to-measure", type=int, default=30)
    return parser.parse_args()


def meter_capacity(beats: int, beat_type: int) -> Fraction:
    return Fraction(beats * 4, beat_type)


def ql_to_divisions(quarter_length: Fraction) -> int:
    return int(quarter_length * DIVISIONS)


def pitch_key(step: str, alter: int | None, octave: int) -> tuple[str, int | None, int]:
    return (step, alter, octave)


def read_pitch(pitch_elem: ET.Element) -> tuple[str, int | None, int]:
    step = pitch_elem.findtext("step", default="C")
    alter_text = pitch_elem.findtext("alter")
    alter = int(alter_text) if alter_text is not None else None
    octave = int(pitch_elem.findtext("octave", default="4"))
    return pitch_key(step, alter, octave)


def effective_duration(note_elem: ET.Element) -> int:
    duration = int(note_elem.findtext("duration", default="0"))
    time_mod = note_elem.find("time-modification")
    if time_mod is None:
        return duration
    actual = int(time_mod.findtext("actual-notes", default="1"))
    normal = int(time_mod.findtext("normal-notes", default="1"))
    return duration * normal // actual


def parse_measure_notes(measure_elem: ET.Element) -> list[SoundEvent]:
    events: list[SoundEvent] = []
    offset_div = 0
    active: SoundEvent | None = None

    for child in list(measure_elem):
        if child.tag != "note":
            continue

        duration_div = effective_duration(child)
        duration = Fraction(duration_div, DIVISIONS)
        is_chord = child.find("chord") is not None
        is_rest = child.find("rest") is not None

        tie_elem = child.find("tie")
        tie_type = tie_elem.get("type") if tie_elem is not None else None

        technical = [
            copy.deepcopy(elem)
            for elem in child.findall("./notations/technical")
        ]
        articulations = [
            copy.deepcopy(elem)
            for elem in child.findall("./notations/articulations/*")
        ]
        stem = child.findtext("stem")

        accidentals: dict[tuple[str, int | None, int], str] = {}
        pitches: list[tuple[str, int | None, int]] = []

        if is_rest:
            if is_chord and active is not None:
                continue
            active = SoundEvent(
                offset=Fraction(offset_div, DIVISIONS),
                duration=duration,
                is_rest=True,
                tie_start=tie_type == "start",
                tie_stop=tie_type == "stop",
            )
            events.append(active)
            if tie_type != "start":
                offset_div += duration_div
            continue

        pitch_elem = child.find("pitch")
        if pitch_elem is None:
            continue
        pitch = read_pitch(pitch_elem)
        pitches.append(pitch)
        accidental = child.findtext("accidental")
        if accidental:
            accidentals[pitch] = accidental

        if is_chord and active is not None:
            active.pitches += tuple(pitches)
            active.accidentals.update(accidentals)
            active.technical.extend(technical)
            active.articulations.extend(articulations)
            if tie_type == "start":
                active.tie_start = True
            if tie_type == "stop":
                active.tie_stop = True
            continue

        active = SoundEvent(
            offset=Fraction(offset_div, DIVISIONS),
            duration=duration,
            pitches=tuple(pitches),
            is_rest=False,
            tie_start=tie_type == "start",
            tie_stop=tie_type == "stop",
            technical=technical,
            accidentals=accidentals,
            articulations=articulations,
            stem=stem,
        )
        events.append(active)
        if tie_type != "start":
            offset_div += duration_div

    return events


def merge_tied_events(events: Iterable[SoundEvent]) -> list[SoundEvent]:
    merged: list[SoundEvent] = []
    for event in events:
        if (
            merged
            and event.pitches
            and merged[-1].pitches == event.pitches
            and not merged[-1].is_rest
            and not event.is_rest
            and merged[-1].tie_start
            and event.tie_stop
        ):
            prev = merged[-1]
            prev.duration += event.duration
            prev.tie_start = False
            prev.tie_stop = event.tie_stop
            if event.technical:
                prev.technical = event.technical
            prev.articulations.extend(event.articulations)
            continue
        clean = copy.deepcopy(event)
        clean.tie_start = False
        clean.tie_stop = False
        merged.append(clean)
    return merged


def split_event(event: SoundEvent, local_start: Fraction, local_end: Fraction) -> SoundEvent | None:
    overlap_start = max(event.offset, local_start)
    overlap_end = min(event.end, local_end)
    if overlap_start >= overlap_end:
        return None

    split = copy.deepcopy(event)
    split.offset = overlap_start - local_start
    split.duration = overlap_end - overlap_start
    split.tie_start = event.offset < local_start
    split.tie_stop = event.end > local_end
    return split


def collect_measure_events(
    timeline: list[SoundEvent],
    measure_start: Fraction,
    measure_end: Fraction,
) -> list[SoundEvent]:
    collected: list[SoundEvent] = []
    for event in timeline:
        split = split_event(event, measure_start, measure_end)
        if split is not None:
            collected.append(split)
    return collected


def choose_time_signature(
    span_ql: Fraction,
    events: list[SoundEvent],
    original_time: tuple[int, int] | None = None,
) -> tuple[int, int]:
    content_end = max((event.end for event in events), default=Fraction(0))
    best: tuple[int, int] | None = None
    best_score = math.inf

    for beats, beat_type in CANDIDATE_METERS:
        capacity = meter_capacity(beats, beat_type)
        if capacity != span_ql:
            continue
        if content_end > capacity + Fraction(1, DIVISIONS):
            continue

        tie_penalty = sum(1 for event in events if event.tie_start or event.tie_stop)
        complexity = abs(beats - 4) + abs(beat_type - 4)
        original_bonus = 0
        if original_time == (beats, beat_type):
            original_bonus = -1
        score = tie_penalty * 10 + complexity + original_bonus
        if score < best_score:
            best_score = score
            best = (beats, beat_type)

    if best is not None:
        return best

    if original_time is not None:
        return original_time

    if span_ql == Fraction(3, 1):
        return (3, 4)
    return (4, 4)


def duration_to_note_parts(duration: Fraction) -> list[tuple[Fraction, int]]:
    remaining = duration
    parts: list[tuple[Fraction, int]] = []

    dotted_values = [
        (Fraction(3, 1), 144),
        (Fraction(2, 1), 96),
        (Fraction(3, 2), 72),
        (Fraction(1, 1), 48),
        (Fraction(1, 2), 24),
        (Fraction(1, 4), 12),
        (Fraction(1, 8), 6),
    ]

    while remaining > Fraction(1, DIVISIONS):
        for ql, div in dotted_values:
            if remaining + Fraction(1, DIVISIONS) >= ql:
                parts.append((ql, div))
                remaining -= ql
                break
        else:
            parts.append((remaining, ql_to_divisions(remaining)))
            break
    return parts


def append_pitch(parent: ET.Element, pitch: tuple[str, int | None, int], accidental: str | None) -> None:
    step, alter, octave = pitch
    pitch_elem = ET.SubElement(parent, "pitch")
    ET.SubElement(pitch_elem, "step").text = step
    if alter is not None:
        ET.SubElement(pitch_elem, "alter").text = str(alter)
    ET.SubElement(pitch_elem, "octave").text = str(octave)
    if accidental:
        ET.SubElement(parent, "accidental").text = accidental


def append_technical(parent: ET.Element, technical_elems: list[ET.Element]) -> None:
    if not technical_elems:
        return
    notations = ET.SubElement(parent, "notations")
    notations.append(copy.deepcopy(technical_elems[0]))


def append_articulations(parent: ET.Element, articulation_elems: list[ET.Element]) -> None:
    if not articulation_elems:
        return
    notations = parent.find("notations")
    if notations is None:
        notations = ET.SubElement(parent, "notations")
    articulations = notations.find("articulations")
    if articulations is None:
        articulations = ET.SubElement(notations, "articulations")
    for articulation in articulation_elems:
        articulations.append(copy.deepcopy(articulation))


def type_from_divisions(duration_div: int) -> tuple[str, bool]:
    for note_type, base in NOTE_TYPES:
        if duration_div == base:
            return note_type, False
        dotted = base + base // 2
        if duration_div == dotted:
            return note_type, True
    if duration_div >= 192:
        return "whole", duration_div != 192
    if duration_div >= 96:
        return "half", duration_div != 96
    if duration_div >= 48:
        return "quarter", duration_div != 48
    if duration_div >= 24:
        return "eighth", duration_div != 24
    if duration_div >= 12:
        return "16th", duration_div != 12
    return "32nd", duration_div != 6


def build_note_elements(
    event: SoundEvent,
    duration_div: int,
    *,
    tie_start: bool,
    tie_stop: bool,
) -> list[ET.Element]:
    note_elems: list[ET.Element] = []

    if event.is_rest:
        note_elems.append(
            build_single_note_element(
                event,
                duration_div,
                is_chord=False,
                tie_start=tie_start,
                tie_stop=tie_stop,
            )
        )
        return note_elems

    for index, pitch in enumerate(event.pitches):
        note_elems.append(
            build_single_note_element(
                event,
                duration_div,
                is_chord=index > 0,
                pitch=pitch,
                tie_start=tie_start if index == 0 else False,
                tie_stop=tie_stop if index == 0 else False,
            )
        )
    return note_elems


def build_single_note_element(
    event: SoundEvent,
    duration_div: int,
    *,
    is_chord: bool,
    pitch: tuple[str, int | None, int] | None = None,
    tie_start: bool,
    tie_stop: bool,
) -> ET.Element:
    note_elem = ET.Element("note")
    if is_chord:
        ET.SubElement(note_elem, "chord")

    if event.is_rest:
        rest = ET.SubElement(note_elem, "rest")
        if duration_div == 144:
            rest.set("measure", "yes")
    else:
        selected_pitch = pitch if pitch is not None else event.pitches[0]
        append_pitch(note_elem, selected_pitch, event.accidentals.get(selected_pitch))

    ET.SubElement(note_elem, "duration").text = str(duration_div)
    note_type, dotted = type_from_divisions(duration_div)
    ET.SubElement(note_elem, "type").text = note_type
    if dotted:
        ET.SubElement(note_elem, "dot")

    if tie_start:
        ET.SubElement(note_elem, "tie", {"type": "start"})
    if tie_stop:
        ET.SubElement(note_elem, "tie", {"type": "stop"})

    if event.stem and not is_chord:
        stem = ET.SubElement(note_elem, "stem")
        stem.text = event.stem

    if event.is_rest:
        if tie_start or tie_stop:
            notations = ET.SubElement(note_elem, "notations")
            if tie_start:
                ET.SubElement(notations, "tied", {"type": "start"})
            if tie_stop:
                ET.SubElement(notations, "tied", {"type": "stop"})
        return note_elem

    if not is_chord:
        append_technical(note_elem, event.technical)
        append_articulations(note_elem, event.articulations)

    if tie_start or tie_stop:
        notations = note_elem.find("notations")
        if notations is None:
            notations = ET.SubElement(note_elem, "notations")
        if tie_start:
            ET.SubElement(notations, "tied", {"type": "start"})
        if tie_stop:
            ET.SubElement(notations, "tied", {"type": "stop"})

    return note_elem


def add_beams(note_elems: list[ET.Element]) -> None:
    beam_group: list[ET.Element] = []

    def flush_group() -> None:
        nonlocal beam_group
        if len(beam_group) >= 2:
            for index, elem in enumerate(beam_group):
                beam = ET.SubElement(elem, "beam", {"number": "1"})
                if index == 0:
                    beam.text = "begin"
                elif index == len(beam_group) - 1:
                    beam.text = "end"
                else:
                    beam.text = "continue"
        beam_group = []

    for note_elem in note_elems:
        if note_elem.find("rest") is not None:
            flush_group()
            continue

        note_type = note_elem.findtext("type", default="")
        if note_type in {"eighth", "16th", "32nd"}:
            beam_group.append(note_elem)
        else:
            flush_group()

    flush_group()


def rebuild_measure_xml(
    original_measure: ET.Element,
    events: list[SoundEvent],
    time_sig: tuple[int, int],
    span_ql: Fraction,
) -> ET.Element:
    measure_number = original_measure.get("number", "1")
    new_measure = ET.Element("measure", {"number": measure_number})

    for child in original_measure:
        if child.tag in {"note", "backup", "attributes"}:
            continue
        new_measure.append(copy.deepcopy(child))

    attributes = None
    for child in original_measure.findall("attributes"):
        attributes = copy.deepcopy(child)
        break
    if attributes is None:
        attributes = ET.Element("attributes")
    else:
        for child in list(attributes):
            if child.tag == "time":
                attributes.remove(child)

    divisions = attributes.find("divisions")
    if divisions is None:
        divisions = ET.SubElement(attributes, "divisions")
    divisions.text = str(DIVISIONS)

    time_elem = ET.SubElement(attributes, "time")
    ET.SubElement(time_elem, "beats").text = str(time_sig[0])
    ET.SubElement(time_elem, "beat-type").text = str(time_sig[1])
    new_measure.append(attributes)

    if not events:
        note_elem = ET.Element("note")
        rest = ET.SubElement(note_elem, "rest")
        rest.set("measure", "yes")
        ET.SubElement(note_elem, "duration").text = str(ql_to_divisions(span_ql))
        ET.SubElement(note_elem, "type").text = "whole"
        new_measure.append(note_elem)
        return new_measure

    if len(events) == 1 and events[0].is_rest and events[0].duration == span_ql:
        note_elem = ET.Element("note")
        rest = ET.SubElement(note_elem, "rest")
        rest.set("measure", "yes")
        duration_div = ql_to_divisions(span_ql)
        ET.SubElement(note_elem, "duration").text = str(duration_div)
        ET.SubElement(note_elem, "type").text = "whole"
        new_measure.append(note_elem)
        return new_measure

    note_elems = []
    current_offset = Fraction(0)
    ordered = sorted(events, key=lambda event: event.offset)

    for event in ordered:
        if event.offset > current_offset:
            gap = event.offset - current_offset
            rest_event = SoundEvent(offset=current_offset, duration=gap, is_rest=True)
            note_elems.extend(
                build_note_elements(
                    rest_event,
                    ql_to_divisions(gap),
                    tie_start=False,
                    tie_stop=False,
                )
            )
            current_offset += gap

        parts = duration_to_note_parts(event.duration)
        for index, (_, part_div) in enumerate(parts):
            tie_start = event.tie_start if index == 0 else False
            tie_stop = event.tie_stop if index == len(parts) - 1 else True
            note_elems.extend(
                build_note_elements(
                    event,
                    part_div,
                    tie_start=tie_start,
                    tie_stop=tie_stop,
                )
            )
        current_offset += event.duration

    if current_offset < span_ql:
        gap = span_ql - current_offset
        rest_event = SoundEvent(offset=current_offset, duration=gap, is_rest=True)
        note_elems.extend(
            build_note_elements(
                rest_event,
                ql_to_divisions(gap),
                tie_start=False,
                tie_stop=False,
            )
        )

    add_beams(note_elems)
    for note_elem in note_elems:
        new_measure.append(note_elem)

    return new_measure


def measure_span_ql(measure_elem: ET.Element, running_time: tuple[int, int] | None) -> tuple[Fraction, tuple[int, int]]:
    time_elem = None
    for attributes in measure_elem.findall("attributes"):
        time_elem = attributes.find("time")
        if time_elem is not None:
            break

    if time_elem is not None:
        beats = int(time_elem.findtext("beats", default="4"))
        beat_type = int(time_elem.findtext("beat-type", default="4"))
        running_time = (beats, beat_type)

    if running_time is None:
        running_time = (4, 4)

    return meter_capacity(running_time[0], running_time[1]), running_time


def build_timeline_from_part(
    part_elem: ET.Element,
    from_measure: int,
    to_measure: int,
    meter_map: dict[int, tuple[int, int]] | None = None,
) -> tuple[list[SoundEvent], list[tuple[Fraction, Fraction, int]]]:
    all_events: list[SoundEvent] = []
    boundaries: list[tuple[Fraction, Fraction, int]] = []
    global_offset = Fraction(0)
    running_time: tuple[int, int] | None = None

    for measure_elem in part_elem.findall("measure"):
        number = int(measure_elem.get("number", "0"))
        if number < from_measure or number > to_measure:
            continue

        if meter_map and number in meter_map:
            running_time = meter_map[number]

        span_ql, running_time = measure_span_ql(measure_elem, running_time)

        measure_events = parse_measure_notes(measure_elem)
        for event in measure_events:
            shifted = copy.deepcopy(event)
            shifted.offset = global_offset + event.offset
            all_events.append(shifted)

        boundaries.append((global_offset, global_offset + span_ql, number))
        global_offset += span_ql

    merged = merge_tied_events(all_events)
    return merged, boundaries


def build_meter_map(part_elem: ET.Element, from_measure: int, to_measure: int) -> dict[int, tuple[int, int]]:
    meters: dict[int, tuple[int, int]] = {}
    running_time: tuple[int, int] | None = None
    for measure_elem in part_elem.findall("measure"):
        number = int(measure_elem.get("number", "0"))
        if number < from_measure or number > to_measure:
            continue
        _, running_time = measure_span_ql(measure_elem, running_time)
        meters[number] = running_time
    return meters


def fix_part_measures(
    part_elem: ET.Element,
    from_measure: int,
    to_measure: int,
    chosen_meters: dict[int, tuple[int, int]] | None = None,
    meter_map: dict[int, tuple[int, int]] | None = None,
) -> tuple[dict[int, ET.Element], dict[int, tuple[int, int]], Fraction]:
    timeline, boundaries = build_timeline_from_part(
        part_elem,
        from_measure,
        to_measure,
        meter_map=meter_map,
    )
    rebuilt: dict[int, ET.Element] = {}
    meters: dict[int, tuple[int, int]] = {}

    for measure_start, measure_end, number in boundaries:
        span_ql = measure_end - measure_start
        events = collect_measure_events(timeline, measure_start, measure_end)
        time_sig = (
            chosen_meters[number]
            if chosen_meters and number in chosen_meters
            else choose_time_signature(
                span_ql,
                events,
                meter_map.get(number) if meter_map else None,
            )
        )
        meters[number] = time_sig
        original = part_elem.find(f"measure[@number='{number}']")
        if original is None:
            raise ValueError(f"Missing measure {number}")
        rebuilt[number] = rebuild_measure_xml(original, events, time_sig, span_ql)

    original_total = sum(end - start for start, end, _ in boundaries)
    return rebuilt, meters, original_total


def count_ties(part_elem: ET.Element, from_measure: int, to_measure: int) -> int:
    count = 0
    for measure_elem in part_elem.findall("measure"):
        number = int(measure_elem.get("number", "0"))
        if from_measure <= number <= to_measure:
            count += len(measure_elem.findall(".//tie"))
    return count


def replace_measure(part_elem: ET.Element, number: int, new_measure: ET.Element) -> None:
    for index, measure_elem in enumerate(part_elem.findall("measure")):
        if int(measure_elem.get("number", "0")) == number:
            part_elem.remove(measure_elem)
            part_elem.insert(index, new_measure)
            return
    raise ValueError(f"Could not replace measure {number}")


def main() -> int:
    args = parse_args()
    part_ids = [part.strip() for part in args.parts.split(",") if part.strip()]

    tree = ET.parse(args.input)
    root = tree.getroot()

    summary: list[str] = []
    chosen_meters: dict[int, tuple[int, int]] | None = None
    meter_map: dict[int, tuple[int, int]] | None = None

    p1_elem = root.find("part[@id='P1']")
    if p1_elem is not None:
        meter_map = build_meter_map(p1_elem, args.from_measure, args.to_measure)

    for pass_index, part_id in enumerate(part_ids):
        part_elem = root.find(f"part[@id='{part_id}']")
        if part_elem is None:
            print(f"Part {part_id} not found", file=sys.stderr)
            return 1

        ties_before = count_ties(part_elem, args.from_measure, args.to_measure)
        rebuilt, meters, original_total = fix_part_measures(
            part_elem,
            args.from_measure,
            args.to_measure,
            chosen_meters=chosen_meters if pass_index > 0 else None,
            meter_map=meter_map,
        )

        if pass_index == 0:
            chosen_meters = meters

        for number, new_measure in rebuilt.items():
            replace_measure(part_elem, number, new_measure)

        ties_after = count_ties(part_elem, args.from_measure, args.to_measure)
        summary.append(
            f"{part_id}: measures {args.from_measure}-{args.to_measure}, "
            f"ties {ties_before}->{ties_after}, total_ql={original_total}"
        )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    ET.indent(tree, space="  ")
    tree.write(args.output, encoding="UTF-8", xml_declaration=True)

    for line in summary:
        print(line)
    print(f"Wrote {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
