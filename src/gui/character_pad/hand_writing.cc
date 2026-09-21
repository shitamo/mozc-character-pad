// Copyright 2010-2018, Google Inc.
// All rights reserved.
//
// Redistribution and use in source and binary forms, with or without
// modification, are permitted provided that the following conditions are
// met:
//
//     * Redistributions of source code must retain the above copyright
// notice, this list of conditions and the following disclaimer.
//     * Redistributions in binary form must reproduce the above
// copyright notice, this list of conditions and the following disclaimer
// in the documentation and/or other materials provided with the
// distribution.
//     * Neither the name of Google Inc. nor the names of its
// contributors may be used to endorse or promote products derived from
// this software without specific prior written permission.
//
// THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
// "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
// LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
// A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
// OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
// SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
// LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
// DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
// THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
// (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
// OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

#include "gui/character_pad/hand_writing.h"

#include <QtGui/QtGui>
#include <QtWidgets/QMessageBox>

#include "base/logging.h"
#include "gui/base/win_util.h"
#include "handwriting/handwriting_manager.h"
#include "handwriting/zinnia_handwriting.h"

namespace mozc {

namespace {
enum HandwritingSourceId {
  kZinniaHandwriting = 0,
};
}  // namespace

namespace gui {

HandWriting::HandWriting(QWidget *parent)
    : QMainWindow(parent),
      zinnia_handwriting_(new mozc::handwriting::ZinniaHandwriting(
          mozc::handwriting::ZinniaHandwriting::GetModelFileName())) {
  setupUi(this);

  handWritingCanvas->setListWidget(resultListWidget);

  fontComboBox->setWritingSystem
      (static_cast<QFontDatabase::WritingSystem>
       (QFontDatabase::Any));
  fontComboBox->setEditable(false);
  fontComboBox->setCurrentFont(resultListWidget->font());

  QObject::connect(resultListWidget,
                   SIGNAL(itemSelected(const QListWidgetItem*)),
                   this,
                   SLOT(itemSelected(const QListWidgetItem*)));

  QObject::connect(fontComboBox,
                   SIGNAL(currentFontChanged(const QFont &)),
                   this, SLOT(updateFont(const QFont &)));

  QObject::connect(sizeComboBox,
                   SIGNAL(currentIndexChanged(int)),
                   this, SLOT(updateFontSize(int)));

  // Cloud handwriting recognition has been removed from the standalone
  // build; only local (zinnia) recognition is available, so the source
  // selector is hidden.
  handwritingSourceComboBox->setVisible(false);
  mozc::handwriting::HandwritingManager::SetHandwritingModule(
      zinnia_handwriting_.get());

  QObject::connect(clearButton,
                   SIGNAL(clicked()),
                   this, SLOT(clear()));

  QObject::connect(revertButton,
                   SIGNAL(clicked()),
                   this, SLOT(revert()));

  QObject::connect(handWritingCanvas,
                   SIGNAL(canvasUpdated()),
                   this, SLOT(updateUIStatus()));

  // "4" means smallest.
  sizeComboBox->setCurrentIndex(4);
  fontComboBox->setCurrentFont(resultListWidget->font());

  handwritingSourceComboBox->setCurrentIndex(kZinniaHandwriting);

  updateUIStatus();
  repaint();
  update();
}

HandWriting::~HandWriting() {}

void HandWriting::updateFont(const QFont &font) {
  resultListWidget->updateFont(font);
}

void HandWriting::updateFontSize(int index) {
  resultListWidget->updateFontSize(index);
}

void HandWriting::resizeEvent(QResizeEvent *event) {
  resultListWidget->update();
}

void HandWriting::clear() {
  resultListWidget->clear();
  handWritingCanvas->clear();
  updateUIStatus();
}

void HandWriting::revert() {
  resultListWidget->clear();
  handWritingCanvas->revert();
  updateUIStatus();
}

void HandWriting::updateUIStatus() {
#ifdef OS_MACOSX
  // Due to a bug of Qt?, the appearance of these buttons
  // doesn't change on Mac. To fix this issue, always set
  // true on Mac.
  clearButton->setEnabled(true);
  revertButton->setEnabled(true);
#else
  const bool enabled = handWritingCanvas->strokes_size() > 0;
  clearButton->setEnabled(enabled);
  revertButton->setEnabled(enabled);
#endif
}

void HandWriting::itemSelected(const QListWidgetItem *item) {
  // Usage-stats reporting to the mozc converter has been removed in the
  // standalone build; the selected candidate is copied to the clipboard by
  // ResultList::mouseReleaseEvent() via SelectionHandler.
}

}  // namespace gui
}  // namespace mozc
