"""Game rules: tokens, the vending machine, and 'no games or storage in a crisis'."""
import analysis
import storage
import vending

CRISIS = {"text": "I want to kill myself", "emotions": [("sadness", 0.9)], "raw_scores": {}, "world": "Blue Hour Tide",
          "final": {"family": "Sadness", "emotion": "sadness", "confidence": 0.9, "unsure": False,
                    "alternatives": [("Sadness", 0.9), ("Fear", 0.05), ("Neutral", 0.05)], "source": "test"},
          "safety": "crisis"}
NORMAL = dict(CRISIS, text="I passed my exam!", safety=None,
              final=dict(CRISIS["final"], family="Joy", emotion="joy"))


# ---------------------------------------------------------------- crisis rules
def test_crisis_disables_games_and_storage(session):
    assert not analysis.games_allowed(CRISIS)
    assert not analysis.may_store(CRISIS)
    assert analysis.games_allowed(NORMAL)


def test_crisis_checkin_is_not_saved_and_earns_no_token(session):
    analysis.record_checkin(CRISIS, "Home")
    assert storage.list_entries() == []
    assert session.tokens == 3 and session.flash == []


def test_normal_checkin_is_saved_and_earns_a_token(session):
    analysis.record_checkin(NORMAL, "Home")
    assert len(storage.list_entries()) == 1
    assert session.tokens == 4


def test_crisis_text_is_never_stored_as_a_correction(session):
    analysis.teach(dict(CRISIS), "Fear", "teach")
    assert storage.list_corrections() == []


def test_journal_switch_off_stops_saving(session):
    storage.set_setting("journal_on", "0")
    analysis.record_checkin(NORMAL, "Home")
    assert storage.list_entries() == []
    assert session.tokens == 4          # the token is still earned
    storage.set_setting("journal_on", "1")


# ---------------------------------------------------------------- vending machine state machine
def start_machine(session, tokens=3):
    vending.ensure_state()
    session.tokens = tokens


def test_ok_without_a_token_is_refused(session):
    start_machine(session)
    vending.press_key("B")
    vending.press_key("2")
    vending.press_ok()
    assert session.vm_state == "idle" and session.vm_message == "INSERT TOKEN"


def test_full_vend_costs_one_token_and_sells_the_slot(session):
    start_machine(session)
    vending.insert_token()
    assert session.tokens == 2 and session.vm_credit
    vending.press_key("B")
    vending.press_key("2")
    vending.press_ok()
    assert session.vm_state == "vending" and "B2" in session.vm_sold and not session.vm_credit
    vending.collect()
    assert session.vm_state == "open" and session.vm_pack["world"]


def test_sold_out_slot_keeps_the_credit(session):
    start_machine(session)
    session.vm_sold = ["A1"]
    vending.insert_token()
    vending.press_key("A")
    vending.press_key("1")
    vending.press_ok()
    assert session.vm_message == "A1 SOLD OUT" and session.vm_credit


def test_cannot_insert_with_no_tokens(session):
    start_machine(session, tokens=0)
    vending.insert_token()
    assert session.vm_message == "NO TOKENS LEFT" and not session.vm_credit


def test_number_before_letter_is_refused(session):
    start_machine(session)
    vending.press_key("1")
    assert session.vm_message == "LETTER FIRST" and session.vm_code == ""


def test_reroll_never_repeats_the_previous_world():
    pack = vending.make_pack()
    for _ in range(50):
        new = vending.make_pack(pack)
        assert new["world"] != pack["world"]
        pack = new
